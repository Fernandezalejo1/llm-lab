import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { AllExceptionsFilter } from './filters/http-exception.filter';

async function bootstrap() {
  const logger = new Logger('Bootstrap');
  const app = await NestFactory.create(AppModule);

  // Global error handler
  app.useGlobalFilters(new AllExceptionsFilter());

  // Security: CORS configurado
  app.enableCors({
    origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true,
    methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-Id'],
  });

  // Global prefix
  app.setGlobalPrefix('api/v1');

  // Validation: sanitizacion global de inputs
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // Swagger / OpenAPI
  const config = new DocumentBuilder()
    .setTitle('Contabilia API')
    .setDescription(
      'Plataforma SaaS de contabilia e IA para estudios contables y PyMEs.\n\n' +
        '## Modulos principales\n' +
        '- **Ingestion** - Carga de extractos bancarios y facturas (CSV/XLSX)\n' +
        '- **Matching** - Motor de conciliacion con reglas + embeddings\n' +
        '- **Cash Application** - Aplicacion de pagos a facturas\n' +
        '- **Learning** - Aprendizaje continuo de alias y patrones\n' +
        '- **Dashboard** - Estadisticas y metricas en tiempo real',
    )
    .setVersion('0.1.0')
    .setLicense('MIT', 'https://github.com/Fernandezalejo1/contabilia/blob/main/LICENSE')
    .addTag('ingestion', 'Carga y procesamiento de archivos')
    .addTag('matching', 'Conciliacion de movimientos bancarios')
    .addTag('dashboard', 'Estadisticas y metricas')
    .addTag('customers', 'Gestion de clientes')
    .addTag('invoices', 'Gestion de facturas')
    .addTag('bank-movements', 'Movimientos bancarios')
    .addServer('http://localhost:3001', 'Desarrollo local')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  // Start
  const port = process.env.PORT || 3001;
  await app.listen(port);
  logger.log(`Contabilia API running on http://localhost:${port}`);
  logger.log(`Swagger docs: http://localhost:${port}/docs`);
}

bootstrap();
