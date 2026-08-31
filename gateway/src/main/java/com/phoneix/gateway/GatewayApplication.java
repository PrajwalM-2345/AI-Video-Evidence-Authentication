package com.phoenix.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
        System.out.println("🦅 Phoenix Enterprise API Gateway Live on Port 8080 — Proxying down to FastAPI Core.");
    }
}