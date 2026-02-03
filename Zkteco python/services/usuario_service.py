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
        
        # Validación especial para user_id (evitar duplicados)
        if 'user_id' in update_data and update_data['user_id'] != db_usuario.user_id:
            usuario_existente = db.query(Usuario).filter(Usuario.user_id == update_data['user_id']).first()
            if usuario_existente:
                logger.error(f"No se puede actualizar user_id: {update_data['user_id']} ya existe")
                return None
                
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
                # LÓGICA DE ASIGNACIÓN DE UID MANUAL (Corrección solicitada)
                # Si el usuario no tiene UID asignado (es nuevo del sistema), calculamos el siguiente
                if not db_usuario.uid:
                    # Buscar el UID máximo actual en la BD
                    # Importar func aquí para evitar circular imports si fuera necesario, o usar SQL directo
                    from sqlalchemy import func
                    max_uid = db.query(func.max(Usuario.uid)).scalar() or 0
                    nuevo_uid = max_uid + 1
                    
                    # Asignar al objeto de BD
                    db_usuario.uid = nuevo_uid
                    db.commit() # Guardar el UID generado
                    logger.info(f"Asignado nuevo UID {nuevo_uid} al usuario {db_usuario.user_id}")

                # Agregar o actualizar usuario en el dispositivo
                success = zk.agregar_usuario(
                    user_id=db_usuario.user_id,
                    name=db_usuario.nombre,
                    privilege=db_usuario.privilegio,
                    password=db_usuario.password or '',
                    group_id=db_usuario.grupo or '',
                    user_id_num=db_usuario.uid # Usar el UID explícito
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
        Sincroniza todos los usuarios desde el dispositivo ZKTeco a la BD (y viceversa)
        
        NUEVA LÓGICA (STRICT MAPPING):
        - Fuente de verdad: Dispositivo (ID Numérico -> UID, Nombre -> Nombre)
        - Matching: EXCLUSIVAMENTE por UID (campo uid en BD).
        - user_id (DNI): SE IGNORA. Si se crea usuario nuevo, user_id=None.
        """
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        
        if not dispositivo:
            return {
                "success": False,
                "message": "Dispositivo no encontrado",
                "usuarios_nuevos_descargados": 0,
                "usuarios_actualizados_bd": 0,
                "usuarios_subidos_dispositivo": 0,
                "errores_subida": 0
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
                    "usuarios_nuevos_descargados": 0,
                    "usuarios_actualizados_bd": 0,
                    "usuarios_subidos_dispositivo": 0,
                    "errores_subida": 0
                }
            
            try:
                usuarios_zk = zk.obtener_usuarios()
                usuarios_nuevos = 0
                usuarios_actualizados = 0
                
                # Mapa actual de usuarios en dispositivo: UID -> Objeto ZK
                mp_usuarios_zk = {}
                
                # ---------------------------------------------------------
                # 1. Descarga (Dispositivo -> BD)
                # ---------------------------------------------------------
                for usuario_zk in usuarios_zk:
                    try:
                        # IMPLEMENTACION SOLICITADA POR USUARIO:
                        # uid (Sistema) = user_id (Biométrico) [Convertido a entero]
                        # user_id (Sistema) = NO SE TOCA / NO RELACIONADO AL BIOMETRICO
                        
                        try:
                            # Convertimos el user_id del biométrico (ej. "42326694") a entero para el UID
                            final_uid = int(usuario_zk.user_id)
                        except ValueError:
                            # Si el user_id del biométrico no es numérico, no podemos usarlo como UID
                            logger.warning(f"Usuario {usuario_zk.name} con ID biometrico '{usuario_zk.user_id}' no es numérico. No se puede mapear a UID sistema.")
                            continue 

                        zk_user_id_str = usuario_zk.user_id # El DNI real
                        
                        # Buscar en BD usando este UID (que ahora es el DNI numérico)
                        db_usuario = db.query(Usuario).filter(
                            Usuario.uid == final_uid
                        ).first()
                        
                        # Fallback: Si no existe por UID, buscar por user_id (DNI) por si acaso ya existía
                        if not db_usuario:
                            db_usuario = db.query(Usuario).filter(
                                Usuario.user_id == zk_user_id_str
                            ).first()
                            if db_usuario:
                                logger.info(f"Usuario encontrado por user_id '{zk_user_id_str}'. Se actualizará su UID a coincidir con el DNI: {final_uid}.")
                        
                        # Preparar datos base (Datos que SIEMPRE se sincronizan desde el dispositivo)
                        datos_usuario = {
                            "nombre": usuario_zk.name,
                            "privilegio": usuario_zk.privilege,
                            "password": usuario_zk.password,
                            "grupo": usuario_zk.group_id,
                            "dispositivo_id": dispositivo_id,
                        }

                        if db_usuario:
                            # Actualizar
                            # 1. EXCLUIMOS 'user_id' (DNI) para no perder el dato del sistema
                            # 2. EXCLUIMOS 'uid' si ya existe, para no perder el índice original
                            
                            # Solo si el usuario en BD no tiene UID (caso raro), le asignamos el nuevo
                            if not db_usuario.uid:
                                datos_usuario["uid"] = final_uid
                            
                            for key, value in datos_usuario.items():
                                setattr(db_usuario, key, value)
                            
                            usuarios_actualizados += 1
                        else:
                            # Crear Nuevo
                            # Solo al crear asignamos user_id y uid iniciales
                            datos_creacion = datos_usuario.copy()
                            datos_creacion["user_id"] = zk_user_id_str
                            datos_creacion["uid"] = final_uid
                            
                            nuevo_usuario = Usuario(**datos_creacion)
                            db.add(nuevo_usuario)
                            usuarios_nuevos += 1
                            
                    except Exception as inner_e:
                        logger.error(f"Error procesando usuario {usuario_zk.uid}: {inner_e}")
                        continue
                
                db.commit()
                
                # ---------------------------------------------------------
                # 2. Subida / Sincronización Inversa (BD -> Dispositivo)
                # ---------------------------------------------------------
                
                # Obtener todos los usuarios de la BD que tienen UID asignado
                # (Los que no tienen UID no se pueden subir fiablemnete sin riesgo de colisión, 
                #  o necesitarían asignación de UID previo)
                usuarios_bd = db.query(Usuario).filter(
                    Usuario.dispositivo_id == dispositivo_id,
                    Usuario.uid != None
                ).all()
                
                usuarios_subidos = 0
                errores_subida = 0
                
                for usuario_bd in usuarios_bd:
                    # Verificar si este UID ya existe en los datos que bajamos del ZK
                    if usuario_bd.uid not in mp_usuarios_zk:
                        try:
                            # Subir usuario al dispositivo
                            logger.info(f"Subiendo usuario faltante al dispositivo: {usuario_bd.nombre} (UID: {usuario_bd.uid})")
                            
                            if zk.agregar_usuario(
                                user_id=str(usuario_bd.uid), # ID en String
                                name=usuario_bd.nombre,
                                privilege=usuario_bd.privilegio,
                                password=usuario_bd.password or '',
                                group_id=usuario_bd.grupo or '',
                                user_id_num=usuario_bd.uid # ID Numérico
                            ):
                                usuarios_subidos += 1
                            else:
                                errores_subida += 1
                                logger.error(f"Fallo al subir usuario UID {usuario_bd.uid}")
                        except Exception as e:
                            errores_subida += 1
                            logger.error(f"Excepción al subir usuario UID {usuario_bd.uid}: {str(e)}")

                return {
                    "success": True,
                    "message": f"Sincronización bidireccional (Modo estricto UID) exitosa",
                    "usuarios_nuevos_descargados": usuarios_nuevos,
                    "usuarios_actualizados_bd": usuarios_actualizados,
                    "usuarios_subidos_dispositivo": usuarios_subidos,
                    "errores_subida": errores_subida
                }
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            db.rollback() 
            logger.error(f"Error al sincronizar usuarios: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "usuarios_nuevos_descargados": 0,
                "usuarios_actualizados_bd": 0,
                "usuarios_subidos_dispositivo": 0,
                "errores_subida": 0
            }
