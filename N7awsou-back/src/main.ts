import { HttpAdapterHost, NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { AllExceptionsFilter } from './all-exception.filter';
import { ValidationPipe } from '@nestjs/common';
import * as cookieParser from 'cookie-parser';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const { httpAdapter } = app.get(HttpAdapterHost);

  // Enable CORS for frontend applications
  app.enableCors({
    origin: "https://n7awsou-platform.vercel.app/",
    credentials: true
  });

  // Use cookie-parser middleware to parse cookies
  app.use(cookieParser());

  app.setGlobalPrefix('api')


  // Apply validation pipeline globally with transformations enabled
  app.useGlobalPipes(new ValidationPipe({
    transform: true,
    transformOptions: {
      enableImplicitConversion: true,
    },
  }));

  // Add request logging middleware for debugging authentication issues

  app.useGlobalFilters(new AllExceptionsFilter(httpAdapter));
  await app.listen(process.env.PORT ?? 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
