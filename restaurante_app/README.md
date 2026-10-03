# 🍽️ Restaurante App - Semana 16: Manejo de Eventos en Tkinter (Gestión de Usuarios con Roles)

Bienvenido a la versión de la **Semana 16** del proyecto **Restaurante App**, correspondiente a la asignatura de **Programación Orientada a Objetos**. En esta entrega se continúa la evolución progresiva de la aplicación de escritorio construida en semanas anteriores, aplicando el **manejo de eventos en Tkinter** dentro de un caso de uso real: la **gestión integral de usuarios con roles y control de acceso**.

Se incorporan eventos virtuales de widgets (`<<TreeviewSelect>>`, `<<ComboboxSelected>>`), eventos de teclado (`<Return>`, `<Escape>`) mediante `bind()`, y botones de acción mediante `command=`, manteniendo una estricta separación de responsabilidades, reutilización de métodos, persistencia en archivos JSON (`usuarios.json`) y recursos visuales profesionales desde `assets/`.

---

## 1. Contexto, Propósito y Objetivos de la Semana 16

El propósito central de esta semana es aplicar de forma práctica el **manejo de eventos en Tkinter**, demostrando cómo la interacción del usuario activa funciones de retorno (**callbacks**) que coordinan la vista y delegan la lógica a la capa de servicios (`RestauranteServicio`), sin saturar la interfaz gráfica con lógica de negocio ni persistencia directa.

### Ciclo de Interacción y Flujo de Eventos
```text
┌─────────────────┐       ┌──────────────────────┐       ┌───────────────────────────────┐
│     USUARIO     │ ────> │  EVENTO (Teclado o   │ ────> │      ENLACE CON bind()        │
│  (Interacción)  │       │   Virtual de ttk)    │       │     o botón con command=      │
└─────────────────┘       └──────────────────────┘       └───────────────┬───────────────┘
                                                                         │
                                                                         ▼
┌───────────────────────────────┐       ┌────────────────────────────────────────────────┐
│      RESPUESTA EN LA UI       │       │             CALLBACK EN LA VISTA               │
│ • Carga reactiva formulario   │ <──── │ • Captura evento / datos de controles          │
│ • Feedback cromático en barra │       │ • Reutiliza métodos sin duplicar lógica        │
│ • Refresco de Treeview        │       └────────────────────────┬───────────────────────┘
└───────────────────────────────┘                                │
                ▲                                                ▼
                │       ┌────────────────────────────────────────────────┐
                │       │              RestauranteServicio               │
                └────── │ • Validaciones de negocio (unicidad, rol, etc) │
                        │ • Reglas de seguridad (anti-autoeliminación)   │
                        │ • Persistencia atómica en usuarios.json        │
                        └────────────────────────────────────────────────┘
```

---

## 2. Evolución del Proyecto respecto a la Semana 15

| Característica / Criterio | Semana 15 (Versión Anterior) | Semana 16 (Versión Actual) |
| :--- | :--- | :--- |
| **Gestión de Usuarios** | Directorio estático de solo lectura. | **CRUD Completo**: Registrar, Consultar, Actualizar y Eliminar usuarios con formulario interactivo y Treeview reactivo. |
| **Modelo de Roles** | Usuarios sin atributo explícito de rol. | **Atributo `rol` en `Usuario`**: `Administrador`, `Empleado` y `Cliente`, serializado y persistido en `usuarios.json`. |
| **Control de Acceso** | Todos los usuarios veían el mismo entorno. | **Segregación de Privilegios**: Solo `Administrador` accede a la gestión de usuarios. Empleados y Clientes reciben pantalla de acceso restringido. |
| **Evento `<<TreeviewSelect>>`**| No implementado en usuarios. | **Selección Reactiva**: Al hacer clic en una fila del Treeview, se consulta al servicio por ID y se cargan sus datos al formulario. |
| **Evento `<Return>` (Enter)** | Solo en pantalla de login. | **Atajo de Teclado**: Confirmación y registro directo de usuario desde los campos del formulario reutilizando el método principal. |
| **Evento `<Escape>` (Esc)** | No implementado. | **Atajo de Cancelación**: Limpia el formulario, deselecciona la fila del Treeview y restablece el estado inicial. |
| **Evento `<<ComboboxSelected>>`**| Usado en selección de productos. | **Selector de Roles**: Actualiza en tiempo real la tarjeta explicativa de privilegios y descripción del rol seleccionado. |
| **Seguridad de Datos** | Sin validaciones específicas de sesión. | **Protección de Cuenta Activa**: La cuenta en sesión no puede auto-eliminarse. Protección de último Administrador. Contraseñas ocultas en Treeview. |
| **Persistencia** | `ventas.json`, `productos.json`, `usuarios.json`. | **Persistencia extendida de usuarios con ID y roles** garantizando integridad entre sesiones. |

---

## 3. Estructura Arquitectónica del Proyecto

El sistema conserva fielmente la arquitectura modular por capas trabajada a lo largo del curso:

```text
restaurante_app/
├── datos/
│   ├── productos.json          # Catálogo gastronómico persistente con existencias (stock)
│   ├── usuarios.json           # Directorio persistente de usuarios, contraseñas y roles
│   └── ventas.json             # Historial persistente de transacciones comerciales
├── modelos/
│   ├── __init__.py
│   ├── producto.py             # Clase Producto (código, nombre, precio, categoría, stock, vender)
│   ├── usuario.py              # Clase Usuario (id_usuario, username, password, nombre, rol, permisos)
│   └── venta.py                # Clase Venta (id_venta, username, código, producto, total, fecha_hora)
├── servicios/
│   ├── __init__.py
│   ├── archivo_servicio.py     # Lectura y escritura segura de archivos JSON con UTF-8
│   └── restaurante_servicio.py # Reglas de negocio, validaciones, CRUD de usuarios/productos y ventas
├── ui/
│   ├── __init__.py
│   ├── login_view.py           # Pantalla de inicio de sesión con logotipo y atajo <Return>
│   └── main_view.py            # Pantalla principal con eventos, roles, Treeviews y formularios
├── assets/                     # [OBLIGATORIO] Recursos visuales y logotipo
│   ├── logo.png                # Logotipo circular de alta resolución del restaurante
│   ├── icon_usuarios.png       # Ícono para la sección de gestión de usuarios
│   ├── icon_ventas.png         # Ícono para la sección de registro de ventas
│   ├── icon_productos.png      # Ícono para la sección de productos
│   └── icon_logout.png         # Ícono para la acción de cerrar sesión
├── main.py                     # Punto de entrada de la aplicación y coordinador de vistas
├── test_servicios.py           # Suite automatizada de pruebas unitarias y de integración (100% OK)
├── generar_assets.py           # Generador autónomo de gráficos PNG nativos
└── README.md                   # Documentación técnica completa del sistema
```

---

## 4. Descripción de los Mecanismos de Manejo de Eventos

La Semana 16 evidencia una clara diferenciación técnica y conceptual entre el uso de `bind()` y el atributo `command=`:

### 4.1. Eventos Virtuales de ttk y de Teclado con `bind()`

El método `bind(secuencia_evento, callback)` asocia una secuencia de evento de Tkinter a una función de retorno que recibe automáticamente un objeto `Event`:

1. **`<<TreeviewSelect>>` (Carga reactiva de usuario al formulario):**
   - **Componente:** `self.tree_usuarios` (ttk.Treeview).
   - **Enlace:** `self.tree_usuarios.bind("<<TreeviewSelect>>", self._on_treeview_usuario_seleccionado)`
   - **Comportamiento:** Al hacer clic sobre cualquier fila del directorio, se extrae el identificador del usuario (`id_usuario`). Se invoca a `RestauranteServicio.consultar_usuario(id_usuario)` para recuperar la entidad completa sin exponer datos confidenciales (como la contraseña) en la tabla visual. Carga los datos en el formulario y activa los botones de edición (`Actualizar` y `Eliminar`).
   
2. **`<Return>` (Atajo de teclado para confirmar registro):**
   - **Componente:** Campos `Entry` de nombre, usuario, contraseña y `Combobox` de rol.
   - **Enlace:** `widget.bind("<Return>", self._on_enter_teclado)`
   - **Comportamiento:** Permite al usuario presionar la tecla **Enter** para procesar el registro inmediatamente. **Reutiliza directamente el método `self._accion_registrar_usuario()`**, garantizando cero duplicación de lógica.

3. **`<Escape>` (Atajo de teclado para limpiar y cancelar):**
   - **Componente:** Formulario, contenedor principal y Treeview.
   - **Enlace:** `widget.bind("<Escape>", self._on_escape_teclado)`
   - **Comportamiento:** Al pulsar la tecla **Esc**, se anula cualquier selección activa en el Treeview (`selection_remove`), se vacían los campos del formulario, se restauran los botones a estado "Nuevo Registro" y se coloca el cursor de foco en el primer campo.

4. **`<<ComboboxSelected>>` (Respuesta dinámica al cambio de rol):**
   - **Componente:** `self.combo_usr_rol` (ttk.Combobox).
   - **Enlace:** `self.combo_usr_rol.bind("<<ComboboxSelected>>", self._on_combobox_rol_seleccionado)`
   - **Comportamiento:** Al cambiar la opción entre `Administrador`, `Empleado` o `Cliente`, se actualiza en tiempo real una tarjeta visual explicativa indicando los privilegios de acceso y responsabilidades de dicho rol en el restaurante.

### 4.2. Botones de Acción con `command=`

Los botones principales de la interfaz utilizan el parámetro `command=callback` para operaciones explícitas disparadas por clic:
- `➕ Registrar Usuario [Enter]` $\to$ `command=self._accion_registrar_usuario`
- `✏️ Actualizar Usuario` $\to$ `command=self._accion_actualizar_usuario`
- `🗑️ Eliminar Usuario` $\to$ `command=self._accion_eliminar_usuario`
- `🧹 Limpiar / Cancelar [Esc]` $\to$ `command=self._limpiar_formulario_usuario`

### 4.3. Comparación Técnica entre `bind()` y `command=`

| Criterio | `command=` | `bind()` |
| :--- | :--- | :--- |
| **Aplicabilidad** | Exclusivo de botones (`Button`, `Checkbutton`, etc.). | Aplicable a **cualquier widget** de Tkinter y ttk. |
| **Parámetro del Callback** | La función asociada no recibe argumentos (`callback()`). | La función asociada recibe obligatoriamente el objeto `event` (`callback(event)`). |
| **Naturaleza del Evento** | Vinculado a la acción primaria del botón (clic). | Soporta eventos de hardware (`<Return>`, `<Escape>`, `<KeyRelease>`) y eventos virtuales (`<<TreeviewSelect>>`, `<<ComboboxSelected>>`). |
| **Múltiples bindings** | Solo un comando activo a la vez. | Permite asociar múltiples manejadores y propagar eventos. |

---

## 5. Gestión de Usuarios, Roles y Reglas de Seguridad

### 5.1. Roles Disponibles en el Sistema

1. **👑 Administrador (`Administrador`):**
   - Posee control total sobre el sistema: gestión administrativa de usuarios (creación, edición, eliminación), catálogo de productos y auditoría de ventas.
2. **👔 Empleado (`Empleado`):**
   - Personal operativo (gerentes, cajeros, meseros): gestiona el registro de ventas comerciales y consulta las existencias de productos. No tiene acceso a la administración de usuarios.
3. **👤 Cliente (`Cliente`):**
   - Clientes registrados: pueden consultar la carta de productos gastronómicos y generar pedidos. Acceso estrictamente restringido frente a la administración.

### 5.2. Control de Acceso Administrativo
- Cuando un usuario con rol de **Administrador** inicia sesión, la barra de navegación le otorga acceso pleno a la **Gestión de Usuarios**, desplegando el formulario interactivo y la tabla Treeview.
- Cuando un usuario con rol de **Empleado** o **Cliente** hace clic en **Gestión de Usuarios**, la interfaz presenta una pantalla estilizada de **Acceso Restringido (🔒)**, impidiendo manipular cuentas ajenas o alterar privilegios.

### 5.3. Reglas de Negocio y Seguridad en `RestauranteServicio`
- **Protección de Cuenta en Sesión Activa:** Un administrador no puede eliminarse a sí mismo por accidente (`usuario.username.lower() == username_en_sesion.lower()`).
- **Protección del Último Administrador:** El sistema impide eliminar o degradar al único administrador registrado, garantizando que el restaurante nunca quede bloqueado sin administración.
- **Unicidad de Usuario:** El `username` no puede repetirse (validación insensible a mayúsculas/minúsculas).
- **Protección de Contraseñas:** Las contraseñas **no se muestran en la tabla Treeview** para evitar fugas visuales de información confidencial. En el formulario se muestran ofuscadas (`•`) con un botón conmutador (`👁️`).

---

## 6. Persistencia de Datos en JSON

Los cambios se almacenan de manera estructurada y persistente con codificación UTF-8:

### Formato de `usuarios.json`:
```json
[
    {
        "id_usuario": "U001",
        "username": "admin",
        "password": "admin123",
        "nombre": "Administrador del Sistema",
        "rol": "Administrador"
    },
    {
        "id_usuario": "U002",
        "username": "gerente",
        "password": "gerente123",
        "nombre": "Gerente del Restaurante",
        "rol": "Empleado"
    },
    {
        "id_usuario": "U003",
        "username": "mesero",
        "password": "mesero123",
        "nombre": "Personal de Atención",
        "rol": "Empleado"
    },
    {
        "id_usuario": "U004",
        "username": "cliente1",
        "password": "cliente123",
        "nombre": "Carlos Mendoza",
        "rol": "Cliente"
    }
]
```

---

## 7. Credenciales de Prueba Disponibles

Para facilitar la verificación del sistema y la evaluación de los criterios de la Semana 16, se suministran las siguientes cuentas preconfiguradas:

| Rol | Usuario | Contraseña | Privilegios / Acceso |
| :--- | :--- | :--- | :--- |
| **👑 Administrador** | `admin` | `admin123` | **Acceso total**: Gestión de Usuarios (CRUD), Productos, Ventas. |
| **👔 Empleado** | `gerente` | `gerente123` | Acceso operativo: Ventas, Productos. Usuarios restringido (🔒). |
| **👔 Empleado** | `mesero` | `mesero123` | Acceso operativo: Ventas, Productos. Usuarios restringido (🔒). |
| **👤 Cliente** | `cliente1` | `cliente123` | Acceso básico: Consulta y ventas. Usuarios restringido (🔒). |

---

## 8. Guía de Ejecución del Proyecto

### Requisitos Previos
- Python 3.9 o superior instalado en el sistema operativo.
- Módulo estándar `tkinter` (incluido por defecto en instalaciones oficiales de Python).
- No requiere librerías externas de terceros (pip).

### Instrucciones para Iniciar la Aplicación
1. Abra una terminal o consola de comandos.
2. Navegue hasta la carpeta del proyecto:
   ```bash
   cd Parcial2/semana16/restaurante_app
   ```
3. Ejecute el archivo principal:
   ```bash
   python main.py
   ```

### Ejecución de la Suite de Pruebas Automatizadas
Para verificar de manera exhaustiva que todos los modelos, servicios, validaciones y reglas de persistencia funcionan sin fallos, ejecute:
```bash
python test_servicios.py
```
*Salida esperada: `🎉 ¡TODAS LAS PRUEBAS AUTOMATIZADAS PASARON EXITOSAMENTE (100%)!`*

---

## 9. Comprobación Mínima de Funcionamiento (Paso a Paso)

1. **Inicio de Sesión:**
   - Ejecute `python main.py`. Se despliega la pantalla de acceso con logotipo e información de roles.
   - Inicie sesión con `admin` / `admin123` (tecla Enter funciona con `<Return>`).
2. **Acceso Administrativo a Usuarios:**
   - Como Administrador, observe la barra superior con el distintivo dorado `[👑 ADMINISTRADOR]`.
   - La sección `Gestión de Usuarios` se abre automáticamente mostrando el formulario y el Treeview.
3. **Registro con Evento `<Return>`:**
   - Ingrese Nombre: `Lucía Torres`, Usuario: `lucia_c`, Contraseña: `lucia123`, Rol: `Empleado`.
   - Pulse la tecla **Enter**. Se ejecuta el registro mediante `<Return>`, actualizándose la tabla y persistiendo en `usuarios.json`.
4. **Selección con Evento `<<TreeviewSelect>>`:**
   - Haga clic sobre la fila recién creada en el Treeview.
   - Se disparará `<<TreeviewSelect>>`, cargando automáticamente los datos de Lucía en el formulario y habilitando los botones `Actualizar` y `Eliminar`.
5. **Respuesta Dinámica con `<<ComboboxSelected>>`:**
   - En el Combobox de rol, cambie a `Cliente`.
   - Observe cómo la tarjeta de información del rol cambia instantáneamente de color y texto explicando los privilegios de Cliente.
6. **Actualización de Usuario:**
   - Modifique el nombre a `Lucía Torres Morales` y presione el botón `✏️ Actualizar`.
   - Se actualiza en la tabla y en el archivo `usuarios.json`.
7. **Limpieza con Evento `<Escape>`:**
   - Presione la tecla **Esc**. Se ejecuta `<Escape>`, limpiando todos los campos, deseleccionando la tabla y volviendo a modo "Nuevo Registro".
8. **Seguridad contra Auto-Eliminación:**
   - Seleccione la fila del usuario `admin` (cuenta en sesión).
   - Intente presionar `🗑️ Eliminar Usuario`. El sistema bloqueará la acción impidiendo eliminar la cuenta en uso.
9. **Verificación de Restricción para No Administradores:**
   - Cierre sesión mediante el botón `🚪 Cerrar Sesión`.
   - Inicie sesión con la cuenta de empleado `gerente` / `gerente123`.
   - Haga clic en el botón `👥 Gestión de Usuarios`.
   - Se presentará la pantalla de **Acceso Restringido (🔒)** impidiendo la gestión administrativa a usuarios no autorizados.

---

## 10. Conclusiones y Cumplimiento de Criterios

- **Modularidad y Reutilización:** Se mantiene la separación limpia de responsabilidades entre datos, modelos, servicios, UI y punto de entrada. Los callbacks delegan en métodos existentes y en el servicio, sin duplicar lógica.
- **Manejo Integral de Eventos:** Se integran `<<TreeviewSelect>>`, `<Return>`, `<Escape>` y `<<ComboboxSelected>>` con enlace mediante `bind()`, diferenciándolos con precisión de los botones gobernados por `command=`.
- **Experiencia de Usuario y Assets:** Se integran componentes con diseño moderno, jerarquía visual, indicadores cromáticos y recursos gráficos desde `assets/`.
- **Persistencia Segura:** Persistencia garantizada en JSON con validaciones que previenen datos corruptos o estados inconsistentes en la base de usuarios del restaurante.
