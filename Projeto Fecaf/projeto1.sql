-- Criar o banco de dados com novo nome
CREATE DATABASE IF NOT EXISTS gastronova;
USE gastronova;

-- Tabela de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    email VARCHAR(100)
);

-- Tabela de restaurantes
CREATE TABLE IF NOT EXISTS restaurantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    mesas INT NOT NULL
);

-- Tabela de cardápios
CREATE TABLE IF NOT EXISTS cardapios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurante_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    vegetariano BOOLEAN DEFAULT FALSE,
    vegano BOOLEAN DEFAULT FALSE,
    carnivoro BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (restaurante_id) REFERENCES restaurantes(id) ON DELETE CASCADE
);

-- Tabela de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    restaurante_id INT NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    qtd_mesas INT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurante_id) REFERENCES restaurantes(id) ON DELETE CASCADE
);
