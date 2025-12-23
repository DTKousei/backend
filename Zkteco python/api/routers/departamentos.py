from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from schemas.departamento import DepartamentoCreate, DepartamentoResponse, DepartamentoUpdate, UsuarioDepartamentoResponse
from services.departamento_service import DepartamentoService

router = APIRouter(prefix="/api/departamentos", tags=["Departamentos"])

@router.get("/", response_model=List[DepartamentoResponse])
def listar_departamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos los departamentos"""
    return DepartamentoService.get_all(db, skip, limit)

@router.post("/", response_model=DepartamentoResponse, status_code=status.HTTP_201_CREATED)
def crear_departamento(departamento: DepartamentoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo departamento"""
    return DepartamentoService.create(db, departamento)

@router.get("/{departamento_id}", response_model=DepartamentoResponse)
def obtener_departamento(departamento_id: int, db: Session = Depends(get_db)):
    """Obtener un departamento por ID"""
    db_dept = DepartamentoService.get_by_id(db, departamento_id)
    if not db_dept:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return db_dept

@router.put("/{departamento_id}", response_model=DepartamentoResponse)
def actualizar_departamento(departamento_id: int, departamento: DepartamentoUpdate, db: Session = Depends(get_db)):
    """Actualizar un departamento"""
    db_dept = DepartamentoService.update(db, departamento_id, departamento)
    if not db_dept:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return db_dept

@router.delete("/{departamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_departamento(departamento_id: int, db: Session = Depends(get_db)):
    """Eliminar un departamento"""
    success = DepartamentoService.delete(db, departamento_id)
    if not success:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return None

@router.post("/{departamento_id}/jefe/{user_dni}", response_model=DepartamentoResponse)
def asignar_jefe(departamento_id: int, user_dni: str, db: Session = Depends(get_db)):
    """Asignar un jefe a un departamento usando su DNI (user_id)"""
    return DepartamentoService.asignar_jefe(db, departamento_id, user_dni)

@router.get("/{departamento_id}/usuarios", response_model=List[UsuarioDepartamentoResponse])
def listar_usuarios_departamento(departamento_id: int, db: Session = Depends(get_db)):
    """Listar usuarios pertenecientes a un departamento"""
    return DepartamentoService.obtener_usuarios(db, departamento_id)

@router.get("/usuario/{user_dni}", response_model=DepartamentoResponse)
def obtener_departamento_usuario(user_dni: str, db: Session = Depends(get_db)):
    """Obtener el departamento de un usuario por su DNI (user_id)"""
    dept = DepartamentoService.obtener_por_usuario_dni(db, user_dni)
    if not dept:
        raise HTTPException(status_code=404, detail="El usuario no tiene departamento asignado")
    return dept
