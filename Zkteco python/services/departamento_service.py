from sqlalchemy.orm import Session
from models.departamento import Departamento
from models.usuario import Usuario
from schemas.departamento import DepartamentoCreate, DepartamentoUpdate
from fastapi import HTTPException
from typing import List

class DepartamentoService:
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Departamento]:
        return db.query(Departamento).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, departamento_id: int) -> Departamento:
        return db.query(Departamento).filter(Departamento.id == departamento_id).first()

    @staticmethod
    def create(db: Session, departamento: DepartamentoCreate) -> Departamento:
        db_departamento = Departamento(**departamento.model_dump())
        db.add(db_departamento)
        db.commit()
        db.refresh(db_departamento)
        return db_departamento

    @staticmethod
    def update(db: Session, departamento_id: int, departamento: DepartamentoUpdate) -> Departamento:
        db_departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
        if not db_departamento:
            return None
        
        update_data = departamento.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_departamento, key, value)
            
        db.commit()
        db.refresh(db_departamento)
        return db_departamento

    @staticmethod
    def delete(db: Session, departamento_id: int) -> bool:
        db_departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
        if not db_departamento:
            return False
        
        db.delete(db_departamento)
        db.commit()
        return True

    @staticmethod
    def asignar_jefe(db: Session, departamento_id: int, user_dni: str) -> Departamento:
        """
        Asigna un usuario (por DNI/user_id) como jefe del departamento.
        """
        # 1. Verificar Dept
        dept = db.query(Departamento).filter(Departamento.id == departamento_id).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        
        # 2. Verificar Usuario (DNI)
        usuario = db.query(Usuario).filter(Usuario.user_id == user_dni).first()
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con DNI {user_dni} no encontrado")
            
        # 3. Asignar
        dept.jefe_id = usuario.user_id
        db.commit()
        db.refresh(dept)
        return dept

    @staticmethod
    def obtener_usuarios(db: Session, departamento_id: int) -> List[Usuario]:
        return db.query(Usuario).filter(Usuario.departamento_id == departamento_id).all()

    @staticmethod
    def obtener_por_usuario_dni(db: Session, user_dni: str) -> Departamento:
        """
        Obtiene el departamento asignado a un usuario por su DNI (user_id)
        """
        usuario = db.query(Usuario).filter(Usuario.user_id == user_dni).first()
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con DNI {user_dni} no encontrado")
        
        if not usuario.departamento_id:
            return None
            
        return usuario.departamento_rel
