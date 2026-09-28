import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { PrismaService } from '@contabilia/database';

/**
 * JWT Auth Guard — verifies Bearer tokens and attaches user to request.
 * In production, replace with @nestjs/passport + passport-jwt.
 */
@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private prisma: PrismaService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new UnauthorizedException('Token de autenticación requerido');
    }

    const token = authHeader.substring(7);
    const payload = this.verifyToken(token);

    if (!payload) {
      throw new UnauthorizedException('Token inválido o expirado');
    }

    const user = await this.prisma.user.findUnique({
      where: { id: payload.userId },
    });

    if (!user || user.status !== 'active') {
      throw new UnauthorizedException('Usuario no válido o desactivado');
    }

    // Attach user to request for downstream use
    request.user = {
      id: user.id,
      email: user.email,
      orgId: payload.orgId,
    };

    return true;
  }

  private verifyToken(token: string): { userId: string; orgId: string } | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64url').toString(),
      );

      // Check expiration
      if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
        return null;
      }

      return {
        userId: payload.sub || payload.userId,
        orgId: payload.orgId || payload.organizationId,
      };
    } catch {
      return null;
    }
  }
}
