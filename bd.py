import sqlite3


class ArticulosBD():
    def conexion(self):
        try:
            conn = sqlite3.connect("stock.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Connection.Error as error:
            print("Error al conectar a la base de datos", error)

    def cerrarConexion(self, conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    def obtenerIdProveedor(self, dic):
        proveedor = dic.get("proveedor")
        if proveedor:
            try:
                conn, cursor = self.conexion()
                cursor.execute("""SELECT id FROM proveedor WHERE nombre = ?""", (proveedor,))
                idProveedor = cursor.fetchone()
                if idProveedor:
                    dic["proveedor"] = idProveedor[0]
                    return dic 
                else: 
                    raise ValueError(f"Proveedor {proveedor} no encontrado!")
            except sqlite3.Error as e:
                raise ValueError(f"Error de base de datos: {e}")
            finally:
                self.cerrarConexion(conn,cursor)
        else: 
            raise ValueError("El campo 'PROVEEDOR' es requerido")

    def agregarArticulo(self,dic):
        articulo = self.obtenerIdProveedor(dic)
        cod = articulo["codigo"]
        cod_interno = articulo["codigoInterno"]
        descrip = articulo["descripcion"]
        cant = articulo["cantidad"]
        id_prov = articulo["proveedor"]
        precio_neto = articulo["precioNeto"]

        if cod and cod_interno and descrip and cant and id_prov and precio_neto:
            conn, cursor = self.conexion()
            try:
                cursor.execute(
                    """INSERT INTO articulo (codigo, codigo_interno, descripcion, cantidad_disponible,
                    id_proveedor, precio_neto) VALUES (?,?,?,?,?,?)""",(cod,cod_interno,descrip,cant,id_prov,precio_neto))
                conn.commit()
                print("Articulos agregados correctamente!")
            
            except sqlite3.Error as e:
                print(f"Hubo un error en la base de datos {e}")
            
            finally:
                self.cerrarConexion(conn, cursor)
        
        else:
            raise ValueError("Todos los campos son requeridos")
                

    def obtenerDatos(self):
        conn,cursor = self.conexion()
        cursor.execute("SELECT * FROM articulo")
        datos = cursor.fetchall()
        self.cerrarConexion(conn, cursor)
        return datos
    
    def obtenerArticulo(self, id):
        conn, cursor = self.conexion()
        cursor.execute("SELECT * FROM ARTICULO WHERE id = ?",(id,))
        articulo = cursor.fetchone()
        self.cerrarConexion(conn, cursor)
        return articulo

    def eliminarDato(self, id_articulo):
        conn, cursor = self.conexion()
        id = id_articulo
        if id:
            try:
                cursor.execute("DELETE FROM articulo WHERE id = ?", (id))
                conn.commit()
                print("Articulo eliminado con exito")
                
            except:
                sqlite3.Connection.OperationalError
                print("Error al eliminar articulo")
            finally:
                self.cerrarConexion(conn,cursor)


    def editarArticulo(self, dic, id):
        articulo = self.obtenerIdProveedor(dic)
        cod = articulo["codigo"]
        cod_interno = articulo["codigoInterno"]
        descrip = articulo["descripcion"]
        cant = articulo["cantidad"]
        id_prov = articulo["proveedor"]
        precio_neto = articulo["precioNeto"]

        if cod and cod_interno and descrip and cant and id_prov and precio_neto and id:
            conn, cursor = self.conexion()
            try:
                cursor.execute("""UPDATE articulo SET codigo = ?, codigo_interno = ?, descripcion = ?,
                                 cantidad_disponible = ?, id_proveedor = ?, precio_neto = ? WHERE id = ?""", (cod,cod_interno,descrip,cant,id_prov,precio_neto, id))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error en la base de datos {e}")

            finally:
                self.cerrarConexion(conn,cursor)
        else:
            raise ValueError("Debes completar todos los campos")


class ProveedoresBD():
    def conexion(self):
        try:
            conn = sqlite3.connect("stock.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Connection.Error as error:
            print("Error al conectar a la base de datos", error)

    def cerrarConexion(self, conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    def obtenerProveedores(self):
        try:
            conn, cursor = self.conexion()
            cursor.execute("""SELECT * FROM proveedor""")
            datos = cursor.fetchall()
            if datos:
                self.cerrarConexion(conn, cursor)
                return datos
        
        except sqlite3.Connection.Error as error:
            print("Error al conectar a la base de datos", error)

    def actualizarProveedor(self, id, descuento, campo):
        try:
            conn, cursor = self.conexion()
            query = f"UPDATE proveedor SET {campo} = ? WHERE id = ?"
            cursor.execute(query, (descuento, id))
            conn.commit()

        except sqlite3.Error as error:
            print("Error al actualizar proveedor", error)
        
        finally: 
            if self.conexion:
                self.cerrarConexion(conn, cursor)