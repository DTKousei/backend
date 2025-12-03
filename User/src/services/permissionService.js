const prisma = require('../config/database.js');

class PermissionService {
    async getAllPermissions() {
        return await prisma.permisos.findMany();
    }

    async getPermissionById(id) {
        const permission = await prisma.permisos.findUnique({
            where: { id }
        });

        if (!permission) throw new Error('Permiso no encontrado');
        return permission;
    }

    async createPermission(data) {
        return await prisma.permisos.create({
            data
        });
    }

    async updatePermission(id, data) {
        return await prisma.permisos.update({
            where: { id },
            data
        });
    }

    async deletePermission(id) {
        return await prisma.permisos.delete({
            where: { id }
        });
    }
}

module.exports = new PermissionService();
