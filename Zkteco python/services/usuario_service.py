"""
Servicio de Usuarios
Lógica de negocio para gestión de usuarios
"""

from sqlalchemy.orm import Session
from models.usuario import Usuario
from models.dispositivo import Dispositivo
from schemas.usuario import UsuarioCreate, UsuarioUpdate
from zkteco_connection import ZKTecoConnection
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class UsuarioService:
    """Servicio para gestión de usuarios"""
    
    @staticmethod
    def crear_usuario(db: Session, usuario: UsuarioCreate, sincronizar: bool = True) -> Optional[Usuario]:
        """
        Crea un nuevo usuario en la base de datos y opcionalmente en el dispositivo
        """
        # Verificar que el dispositivo existe
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == usuario.dispositivo_id).first()
        if not dispositivo:
            logger.error(f"Dispositivo {usuario.dispositivo_id} no encontrado")
            return None
        
        # Verificar que el user_id no exista
        usuario_existente = db.query(Usuario).filter(Usuario.user_id == usuario.user_id).first()
        if usuario_existente:
            logger.error(f"Usuario con user_id {usuario.user_id} ya existe")
            return None
        
        # Crear usuario en base de datos
        db_usuario = Usuario(
            user_id=usuario.user_id,
            nombre=usuario.nombre,
            privilegio=usuario.privilegio,
            password=usuario.password,
            grupo=usuario.grupo,
            dispositivo_id=usuario.dispositivo_id,
            email=usuario.email,
            telefono=usuario.telefono,
            departamento_id=usuario.departamento_id,
            cargo=usuario.cargo,
            fecha_nacimiento=usuario.fecha_nacimiento,
            direccion=usuario.direccion,
            comentarios=usuario.comentarios
        )
        
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        
        # Sincronizar con dispositivo si se solicita
        if sincronizar:
            UsuarioService.sincronizar_usuario_a_dispositivo(db, db_usuario.id)
        
        logger.info(f"Usuario creado: {db_usuario.user_id} - {db_usuario.nombre}")
        return db_usuario
    
    @staticmethod
    def obtener_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID
        """
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    @staticmethod
    def obtener_usuario_por_user_id(db: Session, user_id: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su user_id
        """
        return db.query(Usuario).filter(Usuario.user_id == user_id).first()
    
    @staticmethod
    def obtener_usuarios(db: Session, dispositivo_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtiene lista de usuarios con paginación
        """
        query = db.query(Usuario)
        
        if dispositivo_id is not None:
            query = query.filter(Usuario.dispositivo_id == dispositivo_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_usuario(db: Session, usuario_id: int, usuario_update: UsuarioUpdate, sincronizar: bool = True) -> Optional[Usuario]:
        """
        Actualiza un usuario existente
        """
        db_usuario = UsuarioService.obtener_usuario(db, usuario_id)
        
        if not db_usuario:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = usuario_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_usuario, field, value)
        
        db_usuario.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_usuario)
        
        # Sincronizar con dispositivo si se solicita
        if sincronizar:
            UsuarioService.sincronizar_usuario_a_dispositivo(db, usuario_id)
        
        logger.info(f"Usuario actualizado: {db_usuario.id}")
        return db_usuario
    
    @staticmethod
    def eliminar_usuario(db: Session, usuario_id: int, eliminar_de_dispositivo: bool = True) -> bool:
        """
        Elimina un usuario
        """
        db_usuario = UsuarioService.obtener_usuario(db, usuario_id)
        
        if not db_usuario:
            return False
        
        # Eliminar del dispositivo si se solicita
        if eliminar_de_dispositivo:
            try:
                dispositivo = db_usuario.dispositivo
                zk = ZKTecoConnection(
                    ip_address=dispositivo.ip_address,
                    port=dispositivo.puerto,
                    timeout=dispositivo.timeout,
                    password=dispositivo.password
                )
                
                if zk.conectar():
                    try:
                        zk.eliminar_usuario(db_usuario.user_id)
                    finally:
                        zk.desconectar()
            except Exception as e:
                logger.error(f"Error al eliminar usuario del dispositivo: {str(e)}")
        
        db.delete(db_usuario)
        db.commit()
        
        logger.info(f"Usuario eliminado: {usuario_id}")
        return True
    
    @staticmethod
    def sincronizar_usuario_a_dispositivo(db: Session, usuario_id: int) -> bool:
        """
        Sincroniza un usuario de la BD al dispositivo ZKTeco
        """
        db_usuario = UsuarioService.obtener_usuario(db, usuario_id)
        
        if not db_usuario:
            return False
        
        try:
            dispositivo = db_usuario.dispositivo
            zk = ZKTecoConnection(
                ip_address=dispositivo.ip_address,
                port=dispositivo.puerto,
                timeout=dispositivo.timeout,
                password=dispositivo.password
            )
            
            if not zk.conectar():
                logger.error("No se pudo conectar al dispositivo")
                return False
            
            try:
                # Agregar o actualizar usuario en el dispositivo
                success = zk.agregar_usuario(
                    user_id=db_usuario.user_id,
                    name=db_usuario.nombre,
                    privilege=db_usuario.privilegio,
                    password=db_usuario.password or '',
                    group_id=db_usuario.grupo or '',
                    user_id_num=db_usuario.uid or 0
                )
                
                if success:
                    logger.info(f"Usuario {db_usuario.user_id} sincronizado al dispositivo")
                
                return success
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al sincronizar usuario: {str(e)}")
            return False
    
    @staticmethod
    def sincronizar_usuarios_desde_dispositivo(db: Session, dispositivo_id: int) -> dict:
        """
        Sincroniza todos los usuarios desde el dispositivo ZKTeco a la BD
        """
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        
        if not dispositivo:
            return {
                "success": False,
                "message": "Dispositivo no encontrado",
                "usuarios_nuevos": 0,
                "usuarios_actualizados": 0
            }
        
        try:
            zk = ZKTecoConnection(
                ip_address=dispositivo.ip_address,
                port=dispositivo.puerto,
                timeout=dispositivo.timeout,
                password=dispositivo.password
            )
            
            if not zk.conectar():
                return {
                    "success": False,
                    "message": "No se pudo conectar al dispositivo",
                    "usuarios_nuevos": 0,
                    "usuarios_actualizados": 0
                }
            
            try:
                usuarios_zk = zk.obtener_usuarios()
                usuarios_nuevos = 0
                usuarios_actualizados = 0
                
                for usuario_zk in usuarios_zk:
                    # Buscar si el usuario ya existe
                    db_usuario = db.query(Usuario).filter(
                        Usuario.user_id == usuario_zk.user_id,
                        Usuario.dispositivo_id == dispositivo_id
                    ).first()
                    
                    if db_usuario:
                        # Actualizar usuario existente
                        db_usuario.nombre = usuario_zk.name
                        db_usuario.privilegio = usuario_zk.privilege
                        db_usuario.uid = usuario_zk.uid
                        db_usuario.grupo = usuario_zk.group_id
                        db_usuario.password = usuario_zk.password
                        db_usuario.fecha_actualizacion = datetime.now()
                        usuarios_actualizados += 1
                    else:
                        # Crear nuevo usuario
                        db_usuario = Usuario(
                            user_id=usuario_zk.user_id,
                            uid=usuario_zk.uid,
                            nombre=usuario_zk.name,
                            privilegio=usuario_zk.privilege,
                            password=usuario_zk.password,
                            grupo=usuario_zk.group_id,
                            dispositivo_id=dispositivo_id
                        )
                        db.add(db_usuario)
                        usuarios_nuevos += 1
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Sincronización exitosa",
                    "usuarios_nuevos": usuarios_nuevos,
                    "usuarios_actualizados": usuarios_actualizados
                }
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al sincronizar usuarios: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "usuarios_nuevos": 0,
                "usuarios_actualizados": 0
            }
