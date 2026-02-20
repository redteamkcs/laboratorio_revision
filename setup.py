#!/usr/bin/env python3
"""
Setup script para crear el proyecto Next.js vulnerable
Ejecutar: python setup.py
"""

import os
import json
import shutil
from pathlib import Path

def create_project_structure():
    """Crea la estructura de directorios del proyecto"""
    
    # Directorios a crear
    directories = [
        'pages/api/auth',
        'pages/api/admin',
        'pages/products',
        'pages/admin',
        'components',
        'lib',
        'public/backups',
        'styles'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado directorio: {directory}")

def create_package_json():
    """Crea el package.json con dependencias vulnerables"""
    
    package_json = {
        "name": "vulnerable-next-app",
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint"
        },
        "dependencies": {
            "next": "12.0.0",
            "react": "17.0.2",
            "react-dom": "17.0.2",
            "sqlite3": "5.0.2",
            "express": "4.17.1",
            "jsonwebtoken": "8.5.1",
            "lodash": "4.17.20",
            "axios": "0.21.1",
            "bcrypt": "5.0.1"
        },
        "devDependencies": {
            "eslint": "7.32.0",
            "eslint-config-next": "12.0.0"
        }
    }
    
    with open('package.json', 'w') as f:
        json.dump(package_json, f, indent=2)
    print("✅ Creado package.json")

def create_vulnerable_files():
    """Crea todos los archivos con vulnerabilidades"""
    
    # 1. SQL Injection en products.js
    products_api = '''
// pages/api/products.js
// 🔴 CRÍTICA: SQL Injection
import sqlite3 from 'sqlite3';

export default function handler(req, res) {
  const { category } = req.query;
  const db = new sqlite3.Database('products.db');
  
  // VULNERABLE: Concatenación directa de parámetros
  const query = `SELECT * FROM products WHERE category = '${category}'`;
  
  db.all(query, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
}
'''
    
    with open('pages/api/products.js', 'w') as f:
        f.write(products_api)
    print("✅ Creado pages/api/products.js (SQL Injection)")
    
    # 2. Hardcoded Secrets en auth.js
    auth_lib = '''
// lib/auth.js
// 🔴 CRÍTICA: Hardcoded Secrets
const JWT_SECRET = 'supersecretkey12345';
const ADMIN_PASSWORD = 'admin123';
const API_KEY = 'sk_live_1234567890abcdef';

export function verifyToken(token) {
  try {
    // JWT sin verificación de firma
    const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    return payload;
  } catch (error) {
    return null;
  }
}

export function generateToken(user) {
  // VULNERABLE: Usa secret hardcodeado
  const jwt = require('jsonwebtoken');
  return jwt.sign(user, JWT_SECRET);
}
'''
    
    with open('lib/auth.js', 'w') as f:
        f.write(auth_lib)
    print("✅ Creado lib/auth.js (Hardcoded Secrets)")
    
    # 3. Command Injection en checkout.js
    checkout_api = '''
// pages/api/checkout.js
// 🔴 CRÍTICA: Command Injection
import { exec } from 'child_process';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  const { orderId, email } = req.body;
  
  // VULNERABLE: exec con datos del usuario
  exec(`echo "Order ${orderId} for ${email}" >> orders.log`, (error, stdout, stderr) => {
    if (error) {
      res.status(500).json({ error: error.message });
      return;
    }
    res.json({ success: true, message: "Order processed", output: stdout });
  });
}
'''
    
    with open('pages/api/checkout.js', 'w') as f:
        f.write(checkout_api)
    print("✅ Creado pages/api/checkout.js (Command Injection)")
    
    # 4. Path Traversal en users.js
    users_api = '''
// pages/api/admin/users.js
// 🟠 ALTA: Path Traversal
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const { filename } = req.query;
  
  if (!filename) {
    res.status(400).json({ error: 'Filename required' });
    return;
  }
  
  try {
    // VULNERABLE: Sin sanitización de path
    const data = fs.readFileSync(`./data/${filename}`, 'utf8');
    res.json({ data });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
'''
    
    with open('pages/api/admin/users.js', 'w') as f:
        f.write(users_api)
    print("✅ Creado pages/api/admin/users.js (Path Traversal)")
    
    # 5. XSS en SearchBar.js
    search_component = '''
// components/SearchBar.js
// 🟠 ALTA: XSS (Cross-Site Scripting)
import { useState } from 'react';

export default function SearchBar() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState('');

  const handleSearch = () => {
    // VULNERABLE: innerHTML con datos del usuario
    document.getElementById('search-results').innerHTML = 
      `<h3>Searching for: ${searchTerm}</h3>`;
    
    // Simular búsqueda
    setResults(`Results for: ${searchTerm}`);
  };

  return (
    <div className="search-bar">
      <h2>Search Products</h2>
      <input 
        type="text"
        value={searchTerm} 
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Enter search term..."
      />
      <button onClick={handleSearch}>Search</button>
      <div 
        id="search-results" 
        dangerouslySetInnerHTML={{ __html: results }}
        className="search-results"
      />
    </div>
  );
}
'''
    
    with open('components/SearchBar.js', 'w') as f:
        f.write(search_component)
    print("✅ Creado components/SearchBar.js (XSS)")
    
    # 6. IDOR en [id].js
    product_page = '''
// pages/products/[id].js
// 🟠 ALTA: IDOR (Insecure Direct Object Reference)
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import SearchBar from '../../components/SearchBar';

export default function ProductPage() {
  const router = useRouter();
  const { id } = router.query;
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      // VULNERABLE: Cualquier usuario puede acceder a cualquier producto
      fetch(`/api/products/${id}`)
        .then(res => res.json())
        .then(data => {
          setProduct(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Error:', err);
          setLoading(false);
        });
    }
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!product) return <div>Product not found</div>;

  return (
    <div>
      <h1>{product.name}</h1>
      <p>Price: ${product.price}</p>
      <p>Description: {product.description}</p>
      <SearchBar />
    </div>
  );
}
'''
    
    with open('pages/products/[id].js', 'w') as f:
        f.write(product_page)
    print("✅ Creado pages/products/[id].js (IDOR)")
    
    # 7. No Rate Limiting en login.js
    login_api = '''
// pages/api/auth/login.js
// 🟡 MEDIA: No Rate Limiting
import { generateToken } from '../../../lib/auth';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  const { username, password } = req.body;
  
  // VULNERABLE: Sin límite de intentos
  // Credenciales hardcodeadas para demo
  if (username === 'admin' && password === 'admin123') {
    const token = generateToken({ username, role: 'admin' });
    
    // Cookie sin flags de seguridad
    res.setHeader('Set-Cookie', `token=${token}; HttpOnly`);
    
    res.json({ 
      success: true, 
      token,
      message: 'Login successful'
    });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
}
'''
    
    with open('pages/api/auth/login.js', 'w') as f:
        f.write(login_api)
    print("✅ Creado pages/api/auth/login.js (No Rate Limiting)")
    
    # 8. Information Disclosure en _app.js
    app_file = '''
// pages/_app.js
// 🟡 MEDIA: Information Disclosure
import '../styles/globals.css';

function ErrorBoundary({ children, fallback }) {
  try {
    return children;
  } catch (error) {
    return fallback({ error });
  }
}

function MyApp({ Component, pageProps }) {
  return (
    <div>
      <ErrorBoundary
        fallback={({ error }) => (
          <div style={{ padding: '20px', color: 'red' }}>
            <h1>Application Error</h1>
            <h2>Error: {error?.message}</h2>
            {/* VULNERABLE: Muestra stack trace al usuario */}
            <pre style={{ background: '#f5f5f5', padding: '10px' }}>
              {error?.stack}
            </pre>
          </div>
        )}
      >
        <Component {...pageProps} />
      </ErrorBoundary>
    </div>
  );
}

export default MyApp;
'''
    
    with open('pages/_app.js', 'w') as f:
        f.write(app_file)
    print("✅ Creado pages/_app.js (Info Disclosure)")
    
    # 9. HTTP Response Splitting en checkout.js (versión adicional)
    # (Ya incluido en checkout original)
    
    # 10. Cookie sin flags (ya incluido en login)
    
    # 11. Configuración vulnerable de Next.js
    next_config = '''
// next.config.js
// 🟢 BAJA: TLS/SSL mal configurado
module.exports = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=0' // HSTS deshabilitado
          }
        ]
      }
    ]
  }
}
'''
    
    with open('next.config.js', 'w') as f:
        f.write(next_config)
    print("✅ Creado next.config.js (HSTS deshabilitado)")
    
    # 12. Env file con secrets
    env_file = '''
# .env.local
# ⚠️ EXPUESTO: Secrets en archivo de entorno
DATABASE_URL=postgresql://admin:password123@localhost:5432/prod_db
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
JWT_SECRET=dev_secret_key_12345
ADMIN_API_KEY=admin_sk_live_abcdefghijklmnop
'''
    
    with open('.env.local', 'w') as f:
        f.write(env_file)
    print("✅ Creado .env.local (Secrets expuestos)")
    
    # 13. Backup SQL con datos sensibles
    backup_sql = '''
-- public/backups/backup.sql
-- 🟢 BAJA: Backup de base de datos expuesto
-- Backup automático - DO NOT COMMIT

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password_hash TEXT,
    email TEXT,
    credit_card TEXT
);

INSERT INTO users (id, username, password_hash, email, credit_card) VALUES
(1, 'admin', '5f4dcc3b5aa765d61d8327deb882cf99', 'admin@example.com', '4111111111111111'),
(2, 'john_doe', '5f4dcc3b5aa765d61d8327deb882cf99', 'john@gmail.com', '5555555555554444'),
(3, 'jane_smith', '5f4dcc3b5aa765d61d8327deb882cf99', 'jane@hotmail.com', '378282246310005');

INSERT INTO products (id, name, price, description) VALUES
(1, 'Laptop', 999.99, 'High performance laptop'),
(2, 'Mouse', 29.99, 'Wireless mouse'),
(3, 'Keyboard', 89.99, 'Mechanical keyboard');
'''
    
    with open('public/backups/backup.sql', 'w') as f:
        f.write(backup_sql)
    print("✅ Creado public/backups/backup.sql (Datos expuestos)")
    
    # 14. Index page
    index_page = '''
// pages/index.js
import Link from 'next/link';
import SearchBar from '../components/SearchBar';

export default function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome to Vulnerable Store</h1>
      <p>This is a deliberately vulnerable Next.js application for security testing.</p>
      
      <h2>Features:</h2>
      <ul>
        <li><Link href="/products/1">View Product</Link></li>
        <li><Link href="/admin/dashboard">Admin Dashboard</Link></li>
      </ul>
      
      <h2>Search:</h2>
      <SearchBar />
    </div>
  );
}
'''
    
    with open('pages/index.js', 'w') as f:
        f.write(index_page)
    print("✅ Creado pages/index.js")
    
    # 15. Admin dashboard
    admin_dashboard = '''
// pages/admin/dashboard.js
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function AdminDashboard() {
  const router = useRouter();
  const [users, setUsers] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Verificación débil de admin (solo token en cookie)
    const checkAdmin = async () => {
      const res = await fetch('/api/auth/verify');
      const data = await res.json();
      setIsAdmin(data.isAdmin);
    };
    
    checkAdmin();
  }, []);

  const loadUsers = async () => {
    // Path traversal vulnerable
    const res = await fetch('/api/admin/users?filename=users.json');
    const data = await res.json();
    setUsers(data.users || []);
  };

  if (!isAdmin) {
    return <div>Access Denied</div>;
  }

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <button onClick={loadUsers}>Load Users (Vulnerable)</button>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.username}</li>
        ))}
      </ul>
    </div>
  );
}
'''
    
    with open('pages/admin/dashboard.js', 'w') as f:
        f.write(admin_dashboard)
    print("✅ Creado pages/admin/dashboard.js")
    
    # 16. DB library
    db_lib = '''
// lib/db.js
// Base de datos simulada
const users = [
  { id: 1, username: 'admin', password: 'admin123', role: 'admin' },
  { id: 2, username: 'user', password: 'user123', role: 'user' }
];

const products = [
  { id: 1, name: 'Laptop', price: 999.99, category: 'electronics' },
  { id: 2, name: 'Mouse', price: 29.99, category: 'electronics' },
  { id: 3, name: 'Book', price: 19.99, category: 'books' }
];

export const db = {
  users: {
    findOne: ({ username, password }) => {
      return users.find(u => u.username === username && u.password === password);
    }
  },
  products: {
    findByCategory: (category) => {
      return products.filter(p => p.category === category);
    },
    findById: (id) => {
      return products.find(p => p.id === parseInt(id));
    }
  }
};
'''
    
    with open('lib/db.js', 'w') as f:
        f.write(db_lib)
    print("✅ Creado lib/db.js")
    
    # 17. Global CSS
    css_file = '''
/* styles/globals.css */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  margin: 0;
  padding: 0;
  background: #f5f5f5;
}

.search-bar {
  margin: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-bar input {
  padding: 8px;
  margin-right: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-bar button {
  padding: 8px 16px;
  background: #0070f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-results {
  margin-top: 20px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}
'''
    
    with open('styles/globals.css', 'w') as f:
        f.write(css_file)
    print("✅ Creado styles/globals.css")

def create_readme():
    """Crea el README.md del proyecto"""
    
    readme = '''# Vulnerable Next.js Application

⚠️ **ADVERTENCIA**: Esta aplicación contiene vulnerabilidades intencionales para práctica de revisión de código. NO usar en producción.

## Vulnerabilidades incluidas

### 🔴 CRÍTICAS
1. **SQL Injection** - En endpoint de productos
2. **Hardcoded Secrets** - Credenciales en código
3. **Command Injection** - En proceso de checkout

### 🟠 ALTAS
4. **Path Traversal** - En endpoint admin/users
5. **XSS** - En componente SearchBar
6. **IDOR** - En página de productos

### 🟡 MEDIAS
7. **No Rate Limiting** - En endpoint de login
8. **Information Disclosure** - Stack traces expuestos
9. **Dependencias Vulnerables** - Versiones antiguas

### 🟢 BAJAS
10. **HTTP Response Splitting** - Headers sin sanitizar
11. **Insecure Cookies** - Sin flags de seguridad
12. **HSTS Deshabilitado** - TLS mal configurado

## Instalación

```bash
npm install
npm run dev

Análisis con Semgrep
bash
semgrep --config p/owasp-top-ten --config p/nextjs .
Análisis con SonarQube
bash
sonar-scanner \\
  -Dsonar.projectKey=vulnerable-next-app \\
  -Dsonar.sources=. \\
  -Dsonar.host.url=http://localhost:9000 \\
  -Dsonar.login=your_token
'''
with open('README.md', 'w') as f:
    f.write(readme)
print("✅ Creado README.md")

def main():
    """Función principal"""
    
    print("🚀 Creando proyecto Next.js vulnerable...")
    print("=" * 50)
    
    # Crear estructura
    create_project_structure()
    
    # Crear archivos
    create_package_json()
    create_vulnerable_files()
    create_readme()
    
    print("=" * 50)
    print("✅ Proyecto creado exitosamente!")
    print("\n📁 Estructura del proyecto:")
    print("""
    vulnerable-next-app/
    ├── pages/
    │   ├── api/
    │   │   ├── auth/
    │   │   │   └── login.js
    │   │   ├── checkout.js
    │   │   ├── admin/
    │   │   │   └── users.js
    │   │   └── products.js
    │   ├── products/
    │   │   └── [id].js
    │   ├── admin/
    │   │   └── dashboard.js
    │   ├── _app.js
    │   └── index.js
    ├── components/
    │   └── SearchBar.js
    ├── lib/
    │   ├── db.js
    │   └── auth.js
    ├── public/
    │   └── backups/
    │       └── backup.sql
    ├── styles/
    │   └── globals.css
    ├── .env.local
    ├── next.config.js
    ├── package.json
    └── README.md
    """)
    
    print("\n📝 Para comenzar:")
    print("1. cd vulnerable-next-app")
    print("2. npm install")
    print("3. npm run dev")
    print("\n🔍 Luego ejecuta los análisis:")
    print("- Semgrep: semgrep --config p/owasp-top-ten --config p/nextjs .")
    print("- SonarQube: sonar-scanner (configurado previamente)")
    
    print("\n⚠️  RECUERDA: No subir este código a producción!")

if __name__ == "__main__":
    main()