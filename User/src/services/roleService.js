const prisma = require('../config/database.js');

class RoleService {
    async getAllRoles() {
        return await prisma.roles.findMany({
            include: {
                roles_permisos: {
                    include: {
                        permiso: true
                    }
                }
            }
        });
    }

    async getRoleById(id) {
        const role = await prisma.roles.findUnique({
            where: { id },
            include: {
                roles_permisos: {
                    include: {
                        permiso: true
                    }
                }
            }
        });

        if (!role) throw new Error('Rol no encontrado');
        return role;
    }

    async createRole(data) {
        const { nombre, descripcion, permisos } = data;

        return await prisma.roles.create({
            data: {
                nombre,
                descripcion,
                roles_permisos: {
                    create: permisos?.map(permisoId => ({
                        permiso: { connect: { id: permisoId } }
                    }))
                }
            }
        });
    }

    async updateRole(id, data) {
        const { nombre, descripcion, permisos } = data;

        // Si se actualizan permisos, primero eliminamos los existentes y luego creamos los nuevos
        if (permisos) {
            await prisma.roles_permisos.deleteMany({
                where: { rol_id: id }
            });
        }

        return await prisma.roles.update({
            where: { id },
            data: {
                nombre,
                descripcion,
                roles_permisos: permisos ? {
                    create: permisos.map(permisoId => ({
                        permiso: { connect: { id: permisoId } }
                    }))
                } : undefined
            }
        });
    }

    async deleteRole(id) {
        return await prisma.roles.delete({
            where: { id }
        });
    }
}

module.exports = new RoleService();
