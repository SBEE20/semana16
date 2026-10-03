#!/usr/bin/env python
"""
Suite de pruebas automatizadas para verificar el correcto funcionamiento de
la lógica de negocio, modelo Usuario con roles, operaciones CRUD de usuarios,
validaciones de seguridad (auto-eliminación, último admin), gestión de productos,
ventas y persistencia en archivos JSON (Semana 16).
"""

from pathlib import Path
import sys
import shutil

# Asegurar codificación utf-8 en consola
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DIRECTORIO_RAIZ = Path(__file__).resolve().parent
if str(DIRECTORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_RAIZ))

from modelos.usuario import Usuario
from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio


def ejecutar_pruebas():
    print("=" * 80)
    print("[*] INICIANDO PRUEBAS DE MODELOS, SERVICIOS, EVENTOS Y PERSISTENCIA (SEMANA 16)")
    print("=" * 80)

    # Crear entorno de pruebas aislado para no corromper datos reales
    ruta_datos_real = DIRECTORIO_RAIZ / "datos"
    ruta_datos_test = DIRECTORIO_RAIZ / "datos_test"

    if ruta_datos_test.exists():
        shutil.rmtree(ruta_datos_test)
    shutil.copytree(ruta_datos_real, ruta_datos_test)

    try:
        archivo_servicio = ArchivoServicio(str(ruta_datos_test))
        servicio = RestauranteServicio(archivo_servicio)

        # -------------------------------------------------------------
        # 1. VERIFICACIÓN DEL MODELO USUARIO Y SUS ROLES
        # -------------------------------------------------------------
        print("\n[1] Verificando Modelo Usuario y Roles...")
        usr_admin = Usuario("U099", "superadmin", "clave123", "Super Admin", "Administrador")
        assert usr_admin.es_administrador() is True
        assert usr_admin.es_empleado() is False
        assert usr_admin.es_cliente() is False
        assert usr_admin.validar_credenciales("superadmin", "clave123") is True
        assert usr_admin.validar_credenciales("SUPERADMIN", "clave123") is True  # case-insensitive username
        assert usr_admin.validar_credenciales("superadmin", "clave_mal") is False

        usr_emp = Usuario("U098", "mesero1", "clave123", "Mesero Juan", "Empleado")
        assert usr_emp.es_administrador() is False
        assert usr_emp.es_empleado() is True

        usr_cli = Usuario("U097", "cliente_juan", "clave123", "Juan Perez", "Cliente")
        assert usr_cli.es_cliente() is True

        # Prueba de serialización y deserialización
        dicc = usr_admin.convertir_a_diccionario()
        usr_recuperado = Usuario.desde_diccionario(dicc)
        assert usr_recuperado.username == "superadmin"
        assert usr_recuperado.rol == "Administrador"
        print("    ✓ Modelo Usuario, roles y serialización validados exitosamente.")

        # -------------------------------------------------------------
        # 2. VERIFICACIÓN DE CARGA Y AUTENTICACIÓN
        # -------------------------------------------------------------
        print("\n[2] Verificando Carga Inicial y Autenticación en RestauranteServicio...")
        usuarios = servicio.obtener_usuarios()
        assert len(usuarios) >= 4, f"Se esperaban al menos 4 usuarios, se encontraron {len(usuarios)}"
        print(f"    ✓ {len(usuarios)} usuarios cargados correctamente desde usuarios.json.")

        assert servicio.validar_acceso("admin", "admin123") is True
        assert servicio.validar_acceso("gerente", "gerente123") is True
        assert servicio.validar_acceso("cliente1", "cliente123") is True
        assert servicio.validar_acceso("admin", "clave_falsa") is False
        assert servicio.validar_acceso("", "") is False
        print("    ✓ Autenticación de credenciales verificada.")

        # Verificar roles en servicio
        assert servicio.es_usuario_admin("admin") is True
        assert servicio.es_usuario_admin("gerente") is False
        assert servicio.es_usuario_admin("cliente1") is False
        print("    ✓ Identificación de privilegios de Administrador validada.")

        # -------------------------------------------------------------
        # 3. VERIFICACIÓN DE CONSULTA DE USUARIOS (ID / USERNAME)
        # -------------------------------------------------------------
        print("\n[3] Verificando Consulta de Usuario por ID y por Username...")
        u_por_id = servicio.consultar_usuario("U001")
        assert u_por_id is not None
        assert u_por_id.username == "admin"

        u_por_user = servicio.consultar_usuario("gerente")
        assert u_por_user is not None
        assert u_por_user.id_usuario == "U002"

        assert servicio.consultar_usuario("INEXISTENTE_XYZ") is None
        print("    ✓ Métodos de consulta de usuarios funcionando correctamente.")

        # -------------------------------------------------------------
        # 4. CRUD DE USUARIOS: REGISTRO Y VALIDACIONES
        # -------------------------------------------------------------
        print("\n[4] Verificando Registro de Usuarios y Validaciones de Negocio...")
        # Registro válido de Empleado
        exito, msg, nuevo_u = servicio.registrar_usuario(
            username="cocinero1",
            password="cocina123",
            nombre="Pedro Picapiedra",
            rol="Empleado"
        )
        assert exito is True, f"Fallo al registrar usuario válido: {msg}"
        assert nuevo_u is not None
        assert nuevo_u.username == "cocinero1"
        assert nuevo_u.id_usuario.startswith("U")
        id_cocinero = nuevo_u.id_usuario
        print(f"    ✓ Usuario creado exitosamente: [{id_cocinero}] {nuevo_u.nombre} ({nuevo_u.rol}).")

        # Rechazo por username duplicado
        exito_dup, msg_dup, _ = servicio.registrar_usuario(
            username="cocinero1",
            password="otra_clave",
            nombre="Otro Pedro",
            rol="Empleado"
        )
        assert exito_dup is False
        print(f"    ✓ Control de username duplicado verificado: {msg_dup}")

        # Rechazo por campos vacíos
        exito_vacio, _, _ = servicio.registrar_usuario("", "1234", "Nombre", "Empleado")
        assert exito_vacio is False
        exito_pass_corta, _, _ = servicio.registrar_usuario("user_valido", "12", "Nombre", "Empleado")
        assert exito_pass_corta is False
        print("    ✓ Validaciones de campos obligatorios y longitud mínima verificadas.")

        # -------------------------------------------------------------
        # 5. CRUD DE USUARIOS: ACTUALIZACIÓN
        # -------------------------------------------------------------
        print("\n[5] Verificando Actualización de Usuarios...")
        exito_act, msg_act = servicio.actualizar_usuario(
            id_usuario=id_cocinero,
            nombre="Pedro P. Martinez",
            rol="Cliente",
            password="nueva_clave456"
        )
        assert exito_act is True
        assert nuevo_u.nombre == "Pedro P. Martinez"
        assert nuevo_u.rol == "Cliente"
        assert nuevo_u.validar_credenciales("cocinero1", "nueva_clave456") is True
        print(f"    ✓ Actualización exitosa: {msg_act}")

        # Regla de seguridad: Impedir retirar rol al único administrador
        # "admin" es el único admin por defecto
        exito_deg, msg_deg = servicio.actualizar_usuario(
            id_usuario="U001",
            nombre="Admin Intento Degradar",
            rol="Empleado"
        )
        assert exito_deg is False
        print(f"    ✓ Seguridad: No se permite degradar al único administrador: {msg_deg}")

        # -------------------------------------------------------------
        # 6. CRUD DE USUARIOS: ELIMINACIÓN Y REGLAS DE SEGURIDAD
        # -------------------------------------------------------------
        print("\n[6] Verificando Eliminación y Reglas de Seguridad...")
        # Regla 1: No eliminar la cuenta en sesión activa
        exito_auto, msg_auto = servicio.eliminar_usuario("U001", username_en_sesion="admin")
        assert exito_auto is False
        assert "no puede eliminar la cuenta administrativa" in msg_auto.lower()
        print(f"    ✓ Seguridad: Auto-eliminación bloqueada con éxito: {msg_auto}")

        # Regla 2: No eliminar al único administrador
        exito_del_admin, msg_del_admin = servicio.eliminar_usuario("U001", username_en_sesion="otro_admin")
        assert exito_del_admin is False
        assert "único administrador" in msg_del_admin.lower()
        print(f"    ✓ Seguridad: Eliminación del único admin bloqueada: {msg_del_admin}")

        # Eliminación exitosa de usuario normal
        exito_del, msg_del = servicio.eliminar_usuario(id_cocinero, username_en_sesion="admin")
        assert exito_del is True
        assert servicio.consultar_usuario(id_cocinero) is None
        print(f"    ✓ Eliminación regular exitosa: {msg_del}")

        # -------------------------------------------------------------
        # 7. VERIFICACIÓN DE PERSISTENCIA EN ARCHIVOS JSON
        # -------------------------------------------------------------
        print("\n[7] Verificando Persistencia en Disco (usuarios.json)...")
        # Instanciar un segundo servicio que lea los mismos datos desde el disco
        servicio_relectura = RestauranteServicio(archivo_servicio)
        assert servicio_relectura.consultar_usuario(id_cocinero) is None, "El usuario eliminado no debe persistir en disco"
        assert servicio_relectura.consultar_usuario("U001") is not None, "El administrador debe persistir en disco"
        print("    ✓ Persistencia atómica en usuarios.json verificada al 100%.")

        # -------------------------------------------------------------
        # 8. VERIFICACIÓN DE OPERACIONES DE PRODUCTOS Y VENTAS
        # -------------------------------------------------------------
        print("\n[8] Verificando Continuidad de Productos y Ventas...")
        productos = servicio.obtener_productos()
        assert len(productos) > 0
        p_maito = servicio.consultar_producto("P001")
        assert p_maito is not None
        stock_inicial = p_maito.stock

        # Registrar venta de prueba
        exito_v, msg_v, venta_obj = servicio.registrar_venta(
            username="admin",
            codigo_producto="P001",
            cantidad=2
        )
        assert exito_v is True
        assert venta_obj is not None
        assert p_maito.stock == stock_inicial - 2
        print(f"    ✓ Venta registrada ({venta_obj.id_venta}) y stock actualizado a {p_maito.stock}.")

        print("\n" + "=" * 80)
        print("🎉 ¡TODAS LAS PRUEBAS AUTOMATIZADAS PASARON EXITOSAMENTE (100%)!")
        print("=" * 80)

    finally:
        # Limpiar carpeta temporal de pruebas
        if ruta_datos_test.exists():
            shutil.rmtree(ruta_datos_test)


if __name__ == "__main__":
    ejecutar_pruebas()
