import { plainToInstance } from 'class-transformer';
import { IsString, IsOptional, validateSync } from 'class-validator';

class EnvironmentVariables {
  @IsString()
  DATABASE_URL: string;

  @IsOptional()
  @IsString()
  OPENAI_API_KEY: string;

  @IsOptional()
  @IsString()
  ANTHROPIC_API_KEY: string;

  @IsOptional()
  @IsString()
  NEXT_PUBLIC_API_URL: string;

  @IsOptional()
  @IsString()
  PORT: string;

  @IsOptional()
  @IsString()
  NODE_ENV: string;

  @IsOptional()
  @IsString()
  CORS_ORIGINS: string;
}

export function validate(config: Record<string, unknown>) {
  const validatedConfig = plainToInstance(EnvironmentVariables, config, {
    enableImplicitConversion: true,
  });

  const errors = validateSync(validatedConfig, {
    skipMissingProperties: false,
  });

  if (errors.length > 0) {
    throw new Error(
      'Environment validation error: ' + errors.toString(),
    );
  }

  return validatedConfig;
}
