import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from bd import ArticulosBD, ProveedoresBD
from stock_ui import Ui_MainWindow
from config_ui import Ui_ventana_config as conf
from ag_ed_ui import Ui_Form as ag
import resources

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(lambda: self.cambiar_pagina(0))
        self.ui.pushButton_2.clicked.connect(lambda: self.cambiar_pagina(1))
        self.ui.pushButton_3.clicked.connect(lambda: self.cambiar_pagina(2))
        self.ui.pushButton_4.clicked.connect(lambda: self.cambiar_pagina(3))
        self.ui.pushButton_5.clicked.connect(lambda: self.cambiar_pagina(4))
        self.ui.pushButton_6.clicked.connect(self.agregarArticulo)
        self.ui.pushButton_8.clicked.connect(self.configuracion)
        self.ui.buscar.textChanged.connect(self.filtroDeBusqueda)

        self.agregarDatosTabla()
        

        
    def cambiar_pagina(self, indice):
        self.ui.stackedWidget.setCurrentIndex(indice)

    def agregarDatosTabla(self): 
        print("Actualizando datos de la tabla...")
        bd = ArticulosBD()
        lista_de_datos = bd.obtenerDatos()
        print("Datos obtenidos de la base de datos:", lista_de_datos)
        self.ui.tableWidget.setRowCount(len(lista_de_datos))

        bd = ProveedoresBD()
        proveedores = bd.obtenerProveedores()
        print("Proveedores obtenidos de la base de datos:", proveedores)


        for fila , datos in enumerate(lista_de_datos): 
            for columna, dato in enumerate(datos):
                    item = QtWidgets.QTableWidgetItem(str(dato))
                    self.ui.tableWidget.setItem(fila, columna, item)
                    btnContenedor = QtWidgets.QWidget()
                    layoutBotones = QtWidgets.QHBoxLayout(btnContenedor)
                    layoutBotones.setContentsMargins(0,0,0,0)
                    btnEditar = BotonTabla("Editar", fila)
                    btnEliminar = BotonTabla("Eliminar", fila)
                    btnEditar.clicked.connect(self.editarArticulo)
                    btnEliminar.clicked.connect(self.eliminarArticulo)
                    layoutBotones.addWidget(btnEditar)
                    layoutBotones.addWidget(btnEliminar)
                    self.ui.tableWidget.setCellWidget(fila, 8, btnContenedor)

            for prov in proveedores:
                descuento = prov[3] if prov[3] not in (None, 0) else 1
                ganancia = prov[4] if prov[4] not in (None, 0) else 1
                precio_neto = datos[6] if datos[6] not in (None, 0) else 1

                if descuento == 0 and ganancia == 0:
                    precioP = 1
                    item = QtWidgets.QTableWidgetItem(str(precioP))
                    self.ui.tableWidget.setItem(fila,7,item)
                
                else:
                    precioP = precio_neto - (precio_neto*(descuento/100)) + (precio_neto*(ganancia/100))
                    item = QtWidgets.QTableWidgetItem(str(precioP))
                    self.ui.tableWidget.setItem(fila,7,item)

        self.ui.tableWidget.setColumnHidden(0,True)
        print("Datos de la tabla actualizados...")
        self.ui.tableWidget.viewport().update()

    def filtroDeBusqueda(self):
        texto_filtro = self.ui.buscar.text().lower()
        for fila in range(self.ui.tableWidget.rowCount()):
            mostrar_fila = False
            for columna in range(self.ui.tableWidget.columnCount()):
                item = self.ui.tableWidget.item(fila, columna)
                if item and texto_filtro in item.text().lower():
                    mostrar_fila = True
                    break
            self.ui.tableWidget.setRowHidden(fila, not mostrar_fila)

    def agregarArticulo(self):
        self.ventanaAgregar = VentanaAgregar("Agregar", None)
        self.ventanaAgregar.show()

    def editarArticulo(self):
        boton = self.sender()
        textoBoton = boton.text()
        if isinstance(boton, BotonTabla) and textoBoton == "Editar":
            fila = boton.row
            id_articulo = self.ui.tableWidget.item(fila, 0).text()
            self.agregar= VentanaAgregar("Editar", id_articulo)
            self.agregar.show()
            
    def eliminarArticulo(self):
        boton = self.sender()
        textoBoton = boton.text()

        if isinstance(boton, BotonTabla) and textoBoton == "Eliminar":
            fila = boton.row
            id_articulo = self.ui.tableWidget.item(fila, 3).text()
            confirmacion = QtWidgets.QMessageBox.question(self, "Eliminar articulo", f"¿Estas seguro que quieres eliminar el articulo: {id_articulo}", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)

            if confirmacion == QtWidgets.QMessageBox.StandardButton.Yes:
                bd = ArticulosBD()
                bd.eliminarDato(id_articulo)
                self.ui.tableWidget.removeRow(fila)

            else:
                pass
    
    def configuracion(self):
        self.config = Configuracion()
        self.config.show()

class BotonTabla(QtWidgets.QPushButton):
    def __init__(self, text, row, parent=None):
        super().__init__(text, parent)
        self.row = row

    def obtenerFilaBoton(self, boton):
        boton = self.sender()
        textoBoton = boton.text()
        if isinstance(boton, BotonTabla) and textoBoton == boton:
            fila = boton.row
            id_articulo = self.ui.tableWidget.item(fila, 0).text()
            return id_articulo

class VentanaAgregar(QtWidgets.QWidget):
    def __init__(self, boton, id):
        super().__init__()
        self.boton = boton
        self.id = id
        self.ui = ag()
        self.ui.setupUi(self)

        self.ui.comboBox.addItem("Fabimag")
        self.ui.comboBox.addItem("MW")
        self.ui.comboBox.addItem("Benvenuto")

        self.bd = ArticulosBD()

        self.ui.pushButton_2.clicked.connect(self.close)

        if boton == "Editar":

            try:
                articulo = self.bd.obtenerArticulo(self.id)
                self.ui.lineEdit.setText(str(articulo[1]))
                self.ui.lineEdit_2.setText(str(articulo[2]))
                self.ui.lineEdit_3.setText(str(articulo[3]))
                self.ui.lineEdit_6.setText(str(articulo[4]))
                self.ui.comboBox.setCurrentIndex(articulo[5])
                self.ui.lineEdit_5.setText(str(articulo[6]))
                            
                self.ui.pushButton.clicked.connect(lambda: self.cargarArticuloenBD("Editar", id))


            except Exception as e:
                self.mostrar_mensaje_error(str(e))

        else:
            self.ui.pushButton.clicked.connect(lambda: self.cargarArticuloenBD("Agregar", 9))



    def cargarArticuloenBD(self, boton, id):
        codigo = self.ui.lineEdit.text()
        codigoInterno = self.ui.lineEdit_2.text()
        descripcion = self.ui.lineEdit_3.text()
        cantidad = self.ui.lineEdit_6.text()
        proveedor = self.ui.comboBox.currentText()
        precioNeto = self.ui.lineEdit_5.text()
        dic = {"codigo": f"{codigo}", "codigoInterno": f"{codigoInterno}", "descripcion": f"{descripcion}",
               "cantidad": f"{cantidad}", "proveedor": f"{proveedor}", "precioNeto": f"{precioNeto}" }
        
        if boton == "Editar":
            try:
                bd = ArticulosBD()
                bd.editarArticulo(dic,id)
                window.agregarDatosTabla()
                self.close()

            except Exception as e:
                self.mostrar_mensaje_error(str(e))

        else:
            try:
                bd = ArticulosBD()
                bd.agregarArticulo(dic)
                print(dic)
                window.agregarDatosTabla()
                self.close()

            except Exception as e:
                self.mostrar_mensaje_error(str(e))


    def mostrar_mensaje_error(self, error):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg_box.setText("Error")
        msg_box.setInformativeText(error)
        msg_box.setWindowTitle("Error de Base de Datos")
        msg_box.exec()

class Configuracion(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = conf()
        self.ui.setupUi(self)
        self.initProveedores()

        self.ui.pushButton_guardar.clicked.connect(self.guardarCambios)
        self.ui.pushButton_cancelar.clicked.connect(self.close)

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

            self.ui.gridLayout.addWidget(labelNombre, fila + 1, 0)
            self.ui.gridLayout.addWidget(labelDescuento, fila + 1, 1)
            self.ui.gridLayout.addWidget(labelGanancia, fila + 1, 2)
    
    def actualizarConfigProv(self,lineEdit, campo, id):
        nuevoValor = lineEdit.text()
        bd = ProveedoresBD()
        
        if campo == "descuento":
            bd.actualizarProveedor(id, nuevoValor, "descuento")
        elif campo == "ganancia":
            bd.actualizarProveedor(id, nuevoValor, "ganancia")

    def guardarCambios(self):
        bd = ProveedoresBD()
        self.close()
        return print("Proveedores guardados...")


        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())