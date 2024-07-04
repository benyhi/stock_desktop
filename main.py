import sys
from PySide6 import QtCore, QtWidgets, QtGui, QtSql
from bd import ArticulosBD, ProveedoresBD


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100,100,800,600)
        self.setWindowTitle("Stock")
        self.initUI()
        self.ventanaAgregar = None
        self.ventanaEditar = None
        self.ventanaConfiguraciones = None
        self.ventanaSubirLista = None

    def initUI(self):
        contenidoPrincipal = QtWidgets.QWidget(self)
        self.setCentralWidget(contenidoPrincipal)
        self.layout = QtWidgets.QGridLayout(contenidoPrincipal)
        contenidoPrincipal.setLayout(self.layout)
        btnAgregar = QtWidgets.QPushButton("Agregar Articulo")
        btnConfiguraciones = QtWidgets.QPushButton("Configuraciones")
        btnSubirLista = QtWidgets.QPushButton("Subir lista")
        btnAgregar.clicked.connect(self.agregarArticulo)
        btnConfiguraciones.clicked.connect(self.configuraciones)
        btnSubirLista.clicked.connect(self.subirLista)
        labelBarraBusqueda = QtWidgets.QLabel("Buscar")
        labelBarraBusqueda.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(labelBarraBusqueda,0,1)
        self.barraBusqueda = QtWidgets.QLineEdit()
        self.layout.addWidget(self.barraBusqueda,0,2)
        self.barraBusqueda.textChanged.connect(self.filtroDeBusqueda)
        self.layout.addWidget(btnAgregar, 2,0)
        self.layout.addWidget(btnConfiguraciones, 2,2) 
        self.layout.addWidget(btnSubirLista, 2,1)
        self.crearTabla()

    def crearTabla(self):
        self.tabla = QtWidgets.QTableWidget()
        self.layout.addWidget(self.tabla, 1, 0, 1, 3)
        self.tabla.setColumnCount(9)
        self.tabla.setSortingEnabled(True)
        self.tabla.setHorizontalHeaderLabels(["ID","Codigo","Codigo Interno","Descripcion","Cantidad", "Proveedor", "Precio Neto", "Precio Publico","Acciones"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.agregarDatosTabla()

    def agregarDatosTabla(self): 
        bd = ArticulosBD()
        lista_de_datos = bd.obtenerDatos()
        self.tabla.setRowCount(len(lista_de_datos))

        bd = ProveedoresBD()
        proveedores = bd.obtenerProveedores()

        for fila , datos in enumerate(lista_de_datos): 
            for columna, dato in enumerate(datos):
                item = QtWidgets.QTableWidgetItem(str(dato))
                self.tabla.setItem(fila, columna, item)
                btnContenedor = QtWidgets.QWidget()
                layoutBotones = QtWidgets.QHBoxLayout(btnContenedor)
                layoutBotones.setContentsMargins(0,0,0,0)
                btnEditar = BotonTabla("Editar", fila)
                btnEliminar = BotonTabla("Eliminar", fila)
                btnEditar.clicked.connect(self.editarArticulo)
                btnEliminar.clicked.connect(self.eliminarArticulo)
                layoutBotones.addWidget(btnEditar)
                layoutBotones.addWidget(btnEliminar)
                self.tabla.setCellWidget(fila, 8, btnContenedor)

            for prov in proveedores:
                descuento = prov[3]/100
                ganancia = prov[4]/100
                precio_neto = datos[6]
                precioP = precio_neto - (precio_neto*descuento) + (precio_neto*ganancia)
                item = QtWidgets.QTableWidgetItem(str(precioP))
                self.tabla.setItem(fila,7,item)

        self.tabla.hideColumn(0)

    def filtroDeBusqueda(self):
        texto_filtro = self.barraBusqueda.text().lower()
        for fila in range(self.tabla.rowCount()):
            mostrar_fila = False
            for columna in range(self.tabla.columnCount()):
                item = self.tabla.item(fila, columna)
                if item and texto_filtro in item.text().lower():
                    mostrar_fila = True
                    break
            self.tabla.setRowHidden(fila, not mostrar_fila)

    def agregarArticulo(self):
        self.ventanaAgregar = VentanaAgregar()
        self.ventanaAgregar.show()

    def configuraciones(self):
        self.ventanaConfiguraciones = VentanaConfiguraciones()
        self.ventanaConfiguraciones.show()

    def subirLista(self):
        self.ventanaSubirLista = SubirLista()
        self.ventanaSubirLista.show()

    def eliminarArticulo(self):
        boton = self.sender()
        textoBoton = boton.text()
        if isinstance(boton, BotonTabla) and textoBoton == "Eliminar":
            fila = boton.row
            id_articulo = self.tabla.item(fila, 0).text()
            confirmacion = QtWidgets.QMessageBox.question(self, "Eliminar articulo", f"¿Estas seguro que quieres eliminar el articulo codigo: {id_articulo}", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if confirmacion == QtWidgets.QMessageBox.Yes:
                bd = ArticulosBD()
                bd.eliminarDato(id_articulo)
                self.tabla.removeRow(fila)
            else:
                pass

    def editarArticulo(self):
        boton = self.sender()
        textoBoton = boton.text()
        if isinstance(boton, BotonTabla) and textoBoton == "Editar":
            fila = boton.row
            id_articulo = self.tabla.item(fila, 0).text()
            self.ventanaEditar = VentanaEditar(id_articulo)
            self.ventanaEditar.show()

##############################################################################################
#CLASES AUXILIARES############################################################################
##############################################################################################
#ESTO ES UNA SUBCLASE DE QPUSHBUTTON, QUE CONTIENE UN ATRIBUTO ADICIONAL EN EL CONSTRUCTOR,
#PARA QUE CADA BOTON ALMACENE EL VALOR DE LA FILA EN LA QUE ESTA (SIRVE PARA TABLAS).
##############################################################################################
class BotonTabla(QtWidgets.QPushButton):
    def __init__(self, text, row, parent=None):
        super().__init__(text, parent)
        self.row = row
##############################################################################################

class VentanaEditar(QtWidgets.QWidget):
    def __init__(self, id_articulo):
        super().__init__()
        self.idArticulo = id_articulo
        self.setGeometry(150,150,300,400)
        self.setWindowTitle("Agregar un articulo")
        bd = ArticulosBD()
        articulo = bd.obtenerArticulo(id_articulo)
        self.initUi(articulo)

    def initUi(self, dic): 
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        codigo = dic[1]
        codigo_interno = dic[2]
        descripcion = dic[3]
        cantidad_disponible = dic[4]
        id_proveedor = dic[5]
        precio_neto = dic[6]


        labelCodigoAct = QtWidgets.QLabel("Codigo")
        self.inputCodigoAct = QtWidgets.QLineEdit()
        self.inputCodigoAct.setText(str(codigo))

        labelCodigoInternoAct = QtWidgets.QLabel("Codigo Interno")
        self.inputCodigoInternoAct = QtWidgets.QLineEdit()
        self.inputCodigoInternoAct.setText(str(codigo_interno))

        labelDescripcionAct = QtWidgets.QLabel("Descripcion")
        self.inputDescripcionAct = QtWidgets.QLineEdit()
        self.inputDescripcionAct.setText(str(descripcion))

        labelCantidadAct = QtWidgets.QLabel("Cantidad Disponible")
        self.inputCantidadAct = QtWidgets.QLineEdit()
        self.inputCantidadAct.setValidator(QtGui.QIntValidator())
        self.inputCantidadAct.setText(str(cantidad_disponible))

        labelProveedorAct = QtWidgets.QLabel("Proveedor")
        self.inputProveedorAct = QtWidgets.QComboBox()
        self.inputProveedorAct.addItem("--Seleccionar--")
        self.inputProveedorAct.addItem("Benvenuto")
        self.inputProveedorAct.addItem("Fabimag")
        self.inputProveedorAct.addItem("MW")
        self.inputProveedorAct.setCurrentIndex(int(id_proveedor))

        labelPrecioNetoAct = QtWidgets.QLabel("Precio Neto")
        self.inputPrecioNetoAct = QtWidgets.QLineEdit()
        self.inputPrecioNetoAct.setValidator(QtGui.QIntValidator())
        self.inputPrecioNetoAct.setText(str(precio_neto))
        
        btnAct = QtWidgets.QPushButton("Actualizar Articulo")
        btnAct.clicked.connect(self.editarArticuloenBD)

        self.layout.addWidget(labelCodigoAct,0,0)
        self.layout.addWidget(self.inputCodigoAct, 0, 1)
        self.layout.addWidget(labelCodigoInternoAct,1,0)
        self.layout.addWidget(self.inputCodigoInternoAct,1,1)        
        self.layout.addWidget(labelDescripcionAct,2,0)
        self.layout.addWidget(self.inputDescripcionAct,2,1)
        self.layout.addWidget(labelCantidadAct,3,0)
        self.layout.addWidget(self.inputCantidadAct,3,1)
        self.layout.addWidget(labelProveedorAct,4,0)
        self.layout.addWidget(self.inputProveedorAct,4,1)        
        self.layout.addWidget(labelPrecioNetoAct,5,0)
        self.layout.addWidget(self.inputPrecioNetoAct,5,1)
        self.layout.addWidget(btnAct,6,1)

    def editarArticuloenBD(self):
        codigo = self.inputCodigoAct.text()
        codigoInterno = self.inputCodigoInternoAct.text()
        descripcion = self.inputDescripcionAct.text()
        cantidad = self.inputCantidadAct.text()
        proveedor = self.inputProveedorAct.currentText()
        precioNeto = self.inputPrecioNetoAct.text()
        dic = {"codigo": f"{codigo}", "codigoInterno": f"{codigoInterno}", "descripcion": f"{descripcion}",
               "cantidad": f"{cantidad}", "proveedor": f"{proveedor}", "precioNeto": f"{precioNeto}" }
        bd = ArticulosBD()
        bd.editarArticulo(dic, self.idArticulo)
        self.close()
        ventanaprincipal.agregarDatosTabla()
        print(dic)

class VentanaAgregar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(150,150,300,400)
        self.setWindowTitle("Actualizar un articulo")
        self.initUi()

    def initUi(self): 
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        labelCodigo = QtWidgets.QLabel("Codigo")
        self.inputCodigo = QtWidgets.QLineEdit()
        labelCodigoInterno = QtWidgets.QLabel("Codigo Interno")
        self.inputCodigoInterno = QtWidgets.QLineEdit()
        labelDescripcion = QtWidgets.QLabel("Descripcion")
        self.inputDescripcion = QtWidgets.QLineEdit()
        labelCantidad = QtWidgets.QLabel("Cantidad Disponible")
        self.inputCantidad = QtWidgets.QLineEdit()
        self.inputCantidad.setValidator(QtGui.QIntValidator())
        labelProveedor = QtWidgets.QLabel("Proveedor")
        self.inputProveedor = QtWidgets.QComboBox()
        self.inputProveedor.addItem("--Seleccionar--")
        self.inputProveedor.addItem("Benvenuto")
        self.inputProveedor.addItem("Fabimag")
        self.inputProveedor.addItem("MW")
        labelPrecioNeto = QtWidgets.QLabel("Precio Neto")
        self.inputPrecioNeto = QtWidgets.QLineEdit()
        self.inputPrecioNeto.setValidator(QtGui.QIntValidator())
        btnCargar = QtWidgets.QPushButton("Cargar Articulo")
        btnCargar.clicked.connect(self.cargarArticuloenBD)

        self.layout.addWidget(labelCodigo,0,0)
        self.layout.addWidget(self.inputCodigo, 0, 1)
        self.layout.addWidget(labelCodigoInterno,1,0)
        self.layout.addWidget(self.inputCodigoInterno,1,1)        
        self.layout.addWidget(labelDescripcion,2,0)
        self.layout.addWidget(self.inputDescripcion,2,1)
        self.layout.addWidget(labelCantidad,3,0)
        self.layout.addWidget(self.inputCantidad,3,1)
        self.layout.addWidget(labelProveedor,4,0)
        self.layout.addWidget(self.inputProveedor,4,1)        
        self.layout.addWidget(labelPrecioNeto,5,0)
        self.layout.addWidget(self.inputPrecioNeto,5,1)
        self.layout.addWidget(btnCargar,6,1)

    def cargarArticuloenBD(self):
        codigo = self.inputCodigo.text()
        codigoInterno = self.inputCodigoInterno.text()
        descripcion = self.inputDescripcion.text()
        cantidad = self.inputCantidad.text()
        proveedor = self.inputProveedor.currentText()
        precioNeto = self.inputPrecioNeto.text()
        dic = {"codigo": f"{codigo}", "codigoInterno": f"{codigoInterno}", "descripcion": f"{descripcion}",
               "cantidad": f"{cantidad}", "proveedor": f"{proveedor}", "precioNeto": f"{precioNeto}" }
        bd = ArticulosBD()
        bd.agregarArticulo(dic)
        print(dic)
        self.close()
        ventanaprincipal.agregarDatosTabla()

class VentanaConfiguraciones(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(150,150,300,400)
        self.setWindowTitle("Configuraciones")
        self.initUi()

    def initUi(self): 
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        labelTitulo1 = QtWidgets.QLabel("Proveedor")
        labelTitulo2 = QtWidgets.QLabel("Descuento")
        labelTitulo3 = QtWidgets.QLabel("Ganancia")
        botonGuardar = QtWidgets.QPushButton("Guardar")
        self.layout.addWidget(labelTitulo1,0,0)
        self.layout.addWidget(labelTitulo2,0,1)
        self.layout.addWidget(labelTitulo3,0,2)
        # self.layout.addWidget(botonGuardar,4,2)
        self.initProveedores()
    
    def initProveedores(self):
        bd = ProveedoresBD()
        proveedores = bd.obtenerProveedores()
        for fila , datos in enumerate(proveedores): 
            id = datos[0]
            nombre = datos[1]
            descuento = datos[3]
            ganancia = datos[4]

            labelNombre = QtWidgets.QLabel(str(nombre))
            labelDescuento = QtWidgets.QLineEdit(str(descuento))
            labelGanancia = QtWidgets.QLineEdit(str(ganancia))

            labelDescuento.editingFinished.connect(lambda nuevoDes = labelDescuento, campo ="descuento", pid = id: self.actualizarConfigProv(nuevoDes, campo, pid))
            labelGanancia.editingFinished.connect(lambda nuevoGan = labelGanancia, campo ="ganancia", pid = id: self.actualizarConfigProv(nuevoGan, campo, pid))

            self.layout.addWidget(labelNombre, fila + 1, 0)
            self.layout.addWidget(labelDescuento, fila + 1, 1)
            self.layout.addWidget(labelGanancia, fila + 1, 2)
    
    def actualizarConfigProv(self,lineEdit, campo, id):
        nuevoValor = lineEdit.text()
        bd = ProveedoresBD()
        
        if campo == "descuento":
            bd.actualizarProveedor(id, nuevoValor, "descuento")
        elif campo == "ganancia":
            bd.actualizarProveedor(id, nuevoValor, "ganancia")

class SubirLista(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(150,150,300,400)
        self.setWindowTitle("Subir lista")
        self.initUi()

    def initUi(self): 
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        boton_abrir = QtWidgets.QPushButton("Subir lista")
        boton_abrir.clicked.connect(self.abrirArchivo)
        self.layout.addWidget(boton_abrir)
    def abrirArchivo(self):
        archivo = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
        if archivo:
            print(f'Se seleccionó el archivo: {archivo}')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventanaprincipal = VentanaPrincipal()
    ventanaprincipal.show()
    sys.exit(app.exec())