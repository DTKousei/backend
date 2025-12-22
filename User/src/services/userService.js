const prisma = require('../config/database.js');
const { hashPassword } = require('../utils/password.js');

class UserService {
    async getAllUsers() {
        return await prisma.usuarios.findMany({
            select: {
                id: true,
                usuario: true,
                correo_electronico: true,
                esta_activo: true,
                creado_en: true,
                rol: {
                    select: {
                        id: true,
                        nombre: true
                    }
                }
            }
        });
    }

    async getUserById(id) {
        const user = await prisma.usuarios.findUnique({
            where: { id },
            include: {
                rol: true,
                usuario_permisos: {
                    include: {
                        permiso: true
                    }
                }
            }
        });

        if (!user) throw new Error('Usuario no encontrado');

        // Ocultar hash de contraseña
        const { contrasena_hash, ...userWithoutPassword } = user;
        return userWithoutPassword;
    }

    async getUserByUsername(usuario) {
        const user = await prisma.usuarios.findFirst({
            where: { usuario },
            include: {
                rol: true,
                usuario_permisos: {
                    include: {
                        permiso: true
                    }
                }
            }
        });

        if (!user) throw new Error('Usuario no encontrado');

        // Ocultar hash de contraseña
        const { contrasena_hash, ...userWithoutPassword } = user;
        return userWithoutPassword;
    }

    async createUser(data) {
        const { usuario, correo_electronico, contrasena, rol_id } = data;

        const existingUser = await prisma.usuarios.findFirst({
            where: {
                OR: [
                    { usuario },
                    { correo_electronico }
                ]
            }
        });

        if (existingUser) throw new Error('Usuario o correo ya existe');

        const contrasena_hash = await hashPassword(contrasena);

        return await prisma.usuarios.create({
            data: {
                usuario,
                correo_electronico,
                contrasena_hash,
                rol_id,
                esta_activo: true
            }
        });
    }

    async updateUser(id, data) {
        const { contrasena, ...updateData } = data;

        if (contrasena) {
            updateData.contrasena_hash = await hashPassword(contrasena);
        }

        return await prisma.usuarios.update({
            where: { id },
            data: updateData
        });
    }

    async updateUserByUsername(usuario, data) {
        const { contrasena, ...updateData } = data;

        if (contrasena) {
            updateData.contrasena_hash = await hashPassword(contrasena);
        }

        // Asegurar que no se intente actualizar el campo 'usuario' (que es el ID en este caso)
        // a menos que sea intencional y se maneje la lógica apropiada, pero generalmente el ID no cambia.
        // Si data incluye 'usuario', podría causar conflictos si no se maneja, 
        // pero prisma.update permite actualizar otros campos buscando por 'where'.
        
        return await prisma.usuarios.update({
            where: { usuario },
            data: updateData
        });
    }

    async deleteUser(id) {
        return await prisma.usuarios.delete({
            where: { id }
        });
    }
}

module.exports = new UserService();
