"""
Router de Usuarios
Endpoints para gestión de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse
)
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate,
    sincronizar: bool = Query(True, description="Sincronizar con dispositivo ZKTeco"),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema y opcionalmente en el dispositivo
    """
    db_usuario = UsuarioService.crear_usuario(db, usuario, sincronizar=sincronizar)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el usuario. Verifique que el dispositivo existe y el user_id no esté duplicado"
        )
    return db_usuario


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    dispositivo_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todos los usuarios con paginación
    """
    return UsuarioService.obtener_usuarios(db, dispositivo_id=dispositivo_id, skip=skip, limit=limit)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un usuario específico por ID
    """
    usuario = UsuarioService.obtener_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado"
        )
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    sincronizar: bool = Query(True, description="Sincronizar con dispositivo ZKTeco"),
    db: Session = Depends(get_db)
):
    """
    Actualiza un usuario existente
    """
    usuario = UsuarioService.actualizar_usuario(db, usuario_id, usuario_update, sincronizar=sincronizar)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado"
        )
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    eliminar_de_dispositivo: bool = Query(True, description="Eliminar también del dispositivo ZKTeco"),
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario del sistema
    """
    if not UsuarioService.eliminar_usuario(db, usuario_id, eliminar_de_dispositivo=eliminar_de_dispositivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado"
        )


@router.post("/{usuario_id}/sincronizar")
def sincronizar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Sincroniza un usuario específico con el dispositivo ZKTeco
    """
    if not UsuarioService.sincronizar_usuario_a_dispositivo(db, usuario_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo sincronizar el usuario con el dispositivo"
        )
    return {"message": "Usuario sincronizado exitosamente"}


@router.post("/dispositivos/{dispositivo_id}/sincronizar")
def sincronizar_usuarios_desde_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Sincroniza todos los usuarios desde el dispositivo ZKTeco a la base de datos
    """
    resultado = UsuarioService.sincronizar_usuarios_desde_dispositivo(db, dispositivo_id)
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    return resultado
