# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _

CODES = {
    '0001': u'El comprobante existe y está aceptado',
    '0002': u'El comprobante existe pero está rechazado',
    '0003': u'El comprobante existe pero está de baja',
    '0004': u'Formato de RUC no es válido (debe contener 11 caracteres '
    u'numéricos)',
    '0005': u'Formato del tipo de comprobante no es válido (debe de contener 2'
    'caracteres)',
    '0006': u'Formato de serie inválido (debe contener 4 caracteres)',
    '0007': u'El número de comprobante debe ser mayor que cero',
    '0008': u'El número de RUC no está inscrito en los registros de la SUNAT',
    '0009': u'El tipo de comprobante debe ser (01, 07 o 08)',
    '0010': u'Sólo se puede consultar facturas, notas de crédito y débito'
    u'electrónicas, cuya serie empieza con "F"',
    '0011': u'El comprobante de pago no existe',
    '0012': u'El comprobante de pago electrónico no le pertenece',
    "0100": u'El sistema no puede responder su solicitud. Intente nuevament'
    u'e o comuníquese con su Administrador',
    "0101": u'El encabezado de seguridad es incorrecto',
    "0102": u'Usuario o contraseña incorrectos',
    "0103": u'El Usuario ingresado no existe',
    "0104": u'La Clave ingresada es incorrecta',
    "0105": u'El Usuario no está activo',
    "0106": u'El Usuario no es válido',
    "0109": u'El sistema no puede responder su solicitud. (El servicio de a'
    u'utenticación no está disponible)',
    "0110": u'No se pudo obtener la informacion del tipo de usuario',
    "0111": u'No tiene el perfil para enviar comprobantes electronicos',
    "0112": u'El usuario debe ser secundario',
    "0113": u'El usuario no esta afiliado a Factura Electronica',
    "0125": u'No se pudo obtener la constancia',
    "0126": u'El ticket no le pertenece al usuario',
    "0127": u'El ticket no existe',
    "0130": u'El sistema no puede responder su solicitud. (No se pudo obten'
    u'er el ticket de proceso)',
    "0131": u'El sistema no puede responder su solicitud. (No se pudo graba'
    u'r el archivo en el directorio)',
    "0132": u'El sistema no puede responder su solicitud. (No se pudo graba'
    u'r escribir en el archivo zip)',
    "0133": u'El sistema no puede responder su solicitud. (No se pudo graba'
    u'r la entrada del log)',
    "0134": u'El sistema no puede responder su solicitud. (No se pudo graba'
    u'r en el storage)',
    "0135": u'El sistema no puede responder su solicitud. (No se pudo encol'
    u'ar el pedido)',
    "0136": u'El sistema no puede responder su solicitud. (No se pudo recib'
    u'ir una respuesta del batch)',
    "0137": u'El sistema no puede responder su solicitud. (Se obtuvo una re'
    u'spuesta nula)',
    "0138": u'El sistema no puede responder su solicitud. (Error en Base de'
    u' Datos)',
    "0151": u'El nombre del archivo ZIP es incorrecto',
    "0152": u'No se puede enviar por este método un archivo de resumen',
    "0153": u'No se puede enviar por este método un archivo por lotes',
    "0154": u'El RUC del archivo no corresponde al RUC del usuario o el pro'
    u'veedor no esta autorizado a enviar comprobantes del contribuyente',
    "0155": u'El archivo ZIP esta vacio',
    "0156": u'El archivo ZIP esta corrupto',
    "0157": u'El archivo ZIP no contiene comprobantes',
    "0158": u'El archivo ZIP contiene demasiados comprobantes para este tip'
    u'o de envío',
    "0159": u'El nombre del archivo XML es incorrecto',
    "0160": u'El archivo XML esta vacio',
    "0161": u'El nombre del archivo XML no coincide con el nombre del archi'
    u'vo ZIP',
    "0200": u'No se pudo procesar su solicitud. (Ocurrio un error en el bat'
    u'ch)',
    "0201": u'No se pudo procesar su solicitud. (Llego un requerimiento nul'
    u'o al batch)',
    "0202": u'No se pudo procesar su solicitud. (No llego información del a'
    u'rchivo ZIP)',
    "0203": u'No se pudo procesar su solicitud. (No se encontro archivos en'
    u' la informacion del archivo ZIP)',
    "0204": u'No se pudo procesar su solicitud. (Este tipo de requerimiento'
    u' solo acepta 1 archivo)',
    "0250": u'No se pudo procesar su solicitud. (Ocurrio un error desconoci'
    u'do al hacer unzip)',
    "0251": u'No se pudo procesar su solicitud. (No se pudo crear un direct'
    u'orio para el unzip)',
    "0252": u'No se pudo procesar su solicitud. (No se encontro archivos de'
    u'ntro del zip)',
    "0253": u'No se pudo procesar su solicitud. (No se pudo comprimir la co'
    u'nstancia)',
    "0300": u'No se encontró la raíz documento xml',
    "0301": u'Elemento raiz del xml no esta definido',
    "0302": u'Codigo del tipo de comprobante no registrado',
    "0303": u'No existe el directorio de schemas',
    "0304": u'No existe el archivo de schema',
    "0305": u'El sistema no puede procesar el archivo xml',
    "0306": u'No se puede leer (parsear) el archivo XML',
    "0307": u'No se pudo recuperar la constancia',
    "0400": u'No tiene permiso para enviar casos de pruebas',
    "0401": u'El caso de prueba no existe',
    "0402": u'La numeracion o nombre del documento ya ha sido enviado anter'
    u'iormente',
    "0403": u'El documento afectado por la nota no existe',
    "0404": u'El documento afectado por la nota se encuentra rechazado',
    "1001": u'ID - El dato SERIE-CORRELATIVO no cumple con el formato de ac'
    u'uerdo al tipo de comprobante',
    "1002": u'El XML no contiene informacion en el tag ID',
    "1003": u'InvoiceTypeCode - El valor del tipo de documento es invalido '
    u'o no coincide con el nombre del archivo',
    "1004": u'El XML no contiene el tag o no existe informacion de InvoiceT'
    u'ypeCode',
    "1005": u'CustomerAssignedAccountID -  El dato ingresado no cumple con '
    u'el estandar',
    "1006": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del emisor del documento',
    "1007": u'AdditionalAccountID -  El dato ingresado no cumple con el est'
    u'andar',
    "1008": u'El XML no contiene el tag o no existe informacion de Addition'
    u'alAccountID del emisor del documento',
    "1009": u'IssueDate - El dato ingresado  no cumple con el patron YYYY-M'
    u'M-DD',
    "1010": u'El XML no contiene el tag IssueDate',
    "1011": u'IssueDate- El dato ingresado no es valido',
    "1012": u'ID - El dato ingresado no cumple con el patron SERIE-CORRELAT'
    u'IVO',
    "1013": u'El XML no contiene informacion en el tag ID',
    "1014": u'CustomerAssignedAccountID - El dato ingresado no cumple con e'
    u'l estandar',
    "1015": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del emisor del documento',
    "1016": u'AdditionalAccountID - El dato ingresado no cumple con el esta'
    u'ndar',
    "1017": u'El XML no contiene el tag AdditionalAccountID del emisor del '
    u'documento',
    "1018": u'IssueDate - El dato ingresado no cumple con el patron YYYY-MM'
    u'-DD',
    "1019": u'El XML no contiene el tag IssueDate',
    "1020": u'IssueDate- El dato ingresado no es valido',
    "1021": u'Error en la validacion de la nota de credito',
    "1022": u'La serie o numero del documento modificado por la Nota Electr'
    u'ónica no cumple con el formato establecido',
    "1023": u'No se ha especificado el tipo de documento modificado por la '
    u'Nota electronica',
    "1024": u'CustomerAssignedAccountID - El dato ingresado no cumple con e'
    u'l estandar',
    "1025": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del emisor del documento',
    "1026": u'AdditionalAccountID - El dato ingresado no cumple con el esta'
    u'ndar',
    "1027": u'El XML no contiene el tag AdditionalAccountID del emisor del '
    u'documento',
    "1028": u'IssueDate - El dato ingresado no cumple con el patron YYYY-MM'
    u'-DD',
    "1029": u'El XML no contiene el tag IssueDate',
    "1030": u'IssueDate- El dato ingresado no es valido',
    "1031": u'Error en la validacion de la nota de debito',
    "1032": u'El comprobante fue informado previamente en una comunicacion '
    u'de baja',
    "1033": u'El comprobante fue registrado previamente con otros datos',
    "1034": u'Número de RUC del nombre del archivo no coincide con el consi'
    u'gnado en el contenido del archivo XML',
    "1035": u'Numero de Serie del nombre del archivo no coincide con el con'
    u'signado en el contenido del archivo XML',
    "1036": u'Número de documento en el nombre del archivo no coincide con '
    u'el consignado en el contenido del XML',
    "1037": u'El XML no contiene el tag o no existe informacion de Registra'
    u'tionName del emisor del documento',
    "1038": u'RegistrationName - El nombre o razon social del emisor no cum'
    u'ple con el estandar',
    "1039": u'Solo se pueden recibir notas electronicas que modifican factu'
    u'ras',
    "1040": u'El tipo de documento modificado por la nota electronica no es'
    u' valido',
    "1041": u'cac:PrepaidPayment/cbc:ID - El tag no contiene el atributo @S'
    u'chemaID. que indica el tipo de documento que realiza el anticipo',
    "1042": u'cac:PrepaidPayment/cbc:InstructionID – El tag no contiene el '
    u'atributo @SchemaID. Que indica el tipo de documento del emisor del'
    u' documento del anticipo.',
    "1043": u'cac:OriginatorDocumentReference/cbc:ID - El tag no contiene e'
    u'l atributo @SchemaID. Que indica el tipo de documento del originad'
    u'or del documento electrónico.',
    "1044": u'cac:PrepaidPayment/cbc:InstructionID – El dato ingresado no c'
    u'umple con el estándar.',
    "1045": u'cac:OriginatorDocumentReference/cbc:ID – El dato ingresado no'
    u' cumple con el estándar.',
    "1046": u'cbc:Amount - El dato ingresado no cumple con el estándar.',
    "1047": u'cbc:Quantity - El dato ingresado no cumple con el estándar.',
    "1048": u'El XML no contiene el tag o no existe información de PrepaidA'
    u'mount para un documento con anticipo.',
    "1049": u'ID - Serie y Número del archivo no coincide con el consignado'
    u' en el contenido del XML.',
    "1050": u'El XML no contiene informacion en el tag DespatchAdviceTypeCo'
    u'de.',
    "1051": u'DespatchAdviceTypeCode - El valor del tipo de guía es inválid'
    u'o.',
    "1052": u'DespatchAdviceTypeCode - No coincide con el consignado en el '
    u'contenido del XML.',
    "1053": u'cac:OrderReference - El XML no contiene informacion en serie '
    u'y numero dado de baja (cbc:ID).',
    "1054": u'cac:OrderReference - El valor en numero de documento no cumpl'
    u'e con un formato valido (SERIE-NUMERO).',
    "1055": u'cac:OrderReference - Numero de serie del documento no cumple '
    u'con un formato valido (EG01 ó TXXX).',
    "1056": u'cac:OrderReference - El XML no contiene informacion en el cód'
    u'igo de tipo de documento (cbc:OrderTypeCode).',
    "1057": u'cac:AdditionalDocumentReference - El XML no contiene el tag o'
    u' no existe información en el numero de documento adicional (cbc:ID).',
    "1058": u'cac:AdditionalDocumentReference - El XML no contiene el tag o'
    u' no existe información en el tipo de documento adicional (cbc:Documen'
    u'tTypeCode).',
    "1059": u'El XML no contiene firma digital.',
    "1060": u'cac:Shipment - El XML no contiene el tag o no existe informac'
    u'ion del numero de RUC del Remitente (cac:).',
    "1061": u'El numero de RUC del Remitente no existe.',
    "1062": u'El XML no contiene el atributo o no existe informacion del mo'
    u'tivo de traslado.',
    "1063": u'El valor ingresado como motivo de traslado no es valido.',
    "1064": u'El XML no contiene el atributo o no existe informacion en el '
    u'tag cac:DespatchLine de bienes a transportar.',
    "1065": u'El XML no contiene el atributo o no existe informacion en mod'
    u'alidad de transporte.',
    "1066": u'El XML no contiene el atributo o no existe informacion de dat'
    u'os del transportista.',
    "1067": u'El XML no contiene el atributo o no existe información de veh'
    u'iculos.',
    "1068": u'El XML no contiene el atributo o no existe información de con'
    u'ductores.',
    "1069": u'El XML no contiene el atributo o no existe información de la '
    u'fecha de inicio de traslado o fecha de entrega del bien al transpo'
    u'rtista.',
    "1070": u'El valor ingresado  como fecha de inicio o fecha de entrega a'
    u'l transportista no cumple con el estandar (YYYY-MM-DD).',
    "1071": u'El valor ingresado  como fecha de inicio o fecha de entrega a'
    u'l transportista no es valido.',
    "1072": u'Starttime - El dato ingresado  no cumple con el patron HH:mm:'
    u'ss.SZ.',
    "1073": u'StartTime - El dato ingresado no es valido.',
    "1074": u'cac:Shipment - El XML no contiene o no existe información en '
    u'punto de llegada (cac:DeliveryAddress).',
    "1075": u'cac:Shipment - El XML no contiene o no existe información en '
    u'punto de partida (cac:OriginAddress).',
    "2010": u'El contribuyente no esta activo',
    "2011": u'El contribuyente no esta habido',
    "2012": u'El contribuyente no está autorizado a emitir comprobantes ele'
    u'ctrónicos',
    "2013": u'El contribuyente no cumple con tipo de empresa o tributos req'
    u'ueridos',
    "2014": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del receptor del documento',
    "2015": u'El XML no contiene el tag o no existe informacion de Addition'
    u'alAccountID del receptor del documento',
    "2016": u'AdditionalAccountID -  El dato ingresado  en el tipo de docum'
    u'ento de identidad del receptor no cumple con el estandar o no esta'
    u' permitido.',
    "2017": u'CustomerAssignedAccountID - El numero de documento de identid'
    u'ad del recepetor debe ser  RUC',
    "2018": u'CustomerAssignedAccountID -  El dato ingresado no cumple con '
    u'el estandar',
    "2019": u'El XML no contiene el tag o no existe informacion de Registra'
    u'tionName del emisor del documento',
    "2020": u'RegistrationName - El nombre o razon social del emisor no cum'
    u'ple con el estandar',
    "2021": u'El XML no contiene el tag o no existe informacion de Registra'
    u'tionName del receptor del documento',
    "2022": u'RegistrationName -  El dato ingresado no cumple con el estandar',
    "2023": u'El Numero de orden del item no cumple con el formato establec'
    u'ido',
    "2024": u'El XML no contiene el tag InvoicedQuantity en el detalle de l'
    u'os Items',
    "2025": u'InvoicedQuantity El dato ingresado no cumple con el estandar',
    "2026": u'El XML no contiene el tag cac:Item/cbc:Description en el deta'
    u'lle de los Items',
    "2027": u'El XML no contiene el tag o no existe informacion de cac:Item'
    u'/cbc:Description del item',
    "2028": u'Debe existir el tag cac:AlternativeConditionPrice con un elem'
    u'ento cbc:PriceTypeCode con valor 01',
    "2029": u'PriceTypeCode El dato ingresado no cumple con el estandar',
    "2030": u'El XML no contiene el tag cbc:PriceTypeCode',
    "2031": u'LineExtensionAmount El dato ingresado no cumple con el estandar',
    "2032": u'El XML no contiene el tag LineExtensionAmount en el detalle d'
    u'e los Items',
    "2033": u'El dato ingresado en TaxAmount de la linea no cumple con el f'
    u'ormato establecido',
    "2034": u'TaxAmount es obligatorio',
    "2035": u'cac:TaxCategory/cac:TaxScheme/cbc:ID El dato ingresado no cum'
    u'ple con el estandar',
    "2036": u'El codigo del tributo es invalido',
    "2037": u'El XML no contiene el tag cac:TaxCategory/cac:TaxScheme/cbc:I'
    u'D del Item',
    "2038": u'cac:TaxScheme/cbc:Name del item - No existe el tag o el dato '
    u'ingresado no cumple con el estandar',
    "2039": u'El XML no contiene el tag cac:TaxCategory/cac:TaxScheme/cbc:N'
    u'ame del Item',
    "2040": u'El tipo de afectacion del IGV es incorrecto',
    "2041": u'El sistema de calculo del ISC es incorrecto',
    "2042": u'Debe indicar el IGV. Es un campo obligatorio',
    "2043": u'El dato ingresado en PayableAmount no cumple con el formato e'
    u'stablecido',
    "2044": u'PayableAmount es obligatorio',
    "2045": u'El valor ingresado en AdditionalMonetaryTotal/cbc:ID es incor'
    u'recto',
    "2046": u'AdditionalMonetaryTotal/cbc:ID debe tener valor',
    "2047": u'Es obligatorio al menos un AdditionalMonetaryTotal con codigo'
    u' 1001, 1002, 1003 o 3001',
    "2048": u'El dato ingresado en TaxAmount no cumple con el formato estab'
    u'lecido',
    "2049": u'TaxAmount es obligatorio',
    "2050": u'TaxScheme ID - No existe el tag o el dato ingresado no cumple'
    u' con el estandar',
    "2051": u'El codigo del tributo es invalido',
    "2052": u'El XML no contiene el tag TaxScheme ID de impuestos globales',
    "2053": u'TaxScheme Name - No existe el tag o el dato ingresado no cump'
    u'le con el estandar',
    "2054": u'El XML no contiene el tag TaxScheme Name de impuestos globales',
    "2055": u'TaxScheme TaxTypeCode - El dato ingresado no cumple con el es'
    u'tandar',
    "2056": u'El XML no contiene el tag TaxScheme TaxTypeCode de impuestos '
    u'globales',
    "2057": u'El Name o TaxTypeCode debe corresponder con el Id para el IGV',
    "2058": u'El Name o TaxTypeCode debe corresponder con el Id para el ISC',
    "2059": u'El dato ingresado en TaxSubtotal/cbc:TaxAmount no cumple con '
    u'el formato establecido',
    "2060": u'TaxSubtotal/cbc:TaxAmount es obligatorio',
    "2061": u'El tag global cac:TaxTotal/cbc:TaxAmount debe tener el mismo '
    u'valor que cac:TaxTotal/cac:Subtotal/cbc:TaxAmount',
    "2062": u'El dato ingresado en PayableAmount no cumple con el formato e'
    u'stablecido',
    "2063": u'El XML no contiene el tag PayableAmount',
    "2064": u'El dato ingresado en ChargeTotalAmount no cumple con el forma'
    u'to establecido',
    "2065": u'El dato ingresado en el campo Total Descuentos no cumple con '
    u'el formato establecido',
    "2066": u'Debe indicar una descripcion para el tag sac:AdditionalProper'
    u'ty/cbc:Value',
    "2067": u'cac:Price/cbc:PriceAmount - El dato ingresado no cumple con e'
    u'l estandar',
    "2068": u'El XML no contiene el tag cac:Price/cbc:PriceAmount en el det'
    u'alle de los Items',
    "2069": u'DocumentCurrencyCode - El dato ingresado no cumple con la est'
    u'ructura',
    "2070": u'El XML no contiene el tag o no existe informacion de Document'
    u'CurrencyCode',
    "2071": u'La moneda debe ser la misma en todo el documento',
    "2072": u'CustomizationID - La versión del documento no es la correcta',
    "2073": u'El XML no contiene el tag o no existe informacion de Customiz'
    u'ationID',
    "2074": u'UBLVersionID - La versión del UBL no es correcta',
    "2075": u'El XML no contiene el tag o no existe informacion de UBLVersi'
    u'onID',
    "2076": u'cac:Signature/cbc:ID - Falta el identificador de la firma',
    "2077": u'El tag cac:Signature/cbc:ID debe contener informacion',
    "2078": u'cac:Signature/cac:SignatoryParty/cac:PartyIdentification/cbc:'
    u'ID - Debe ser igual al RUC del emisor',
    "2079": u'El XML no contiene el tag cac:Signature/cac:SignatoryParty/ca'
    u'c:PartyIdentification/cbc:ID',
    "2080": u'cac:Signature/cac:SignatoryParty/cac:PartyName/cbc:Name - No '
    u'cumple con el estandar',
    "2081": u'El XML no contiene el tag cac:Signature/cac:SignatoryParty/ca'
    u'c:PartyName/cbc:Name',
    "2082": u'cac:Signature/cac:DigitalSignatureAttachment/cac:ExternalRefe'
    u'rence/cbc:URI - No cumple con el estandar',
    "2083": u'El XML no contiene el tag cac:Signature/cac:DigitalSignatureA'
    u'ttachment/cac:ExternalReference/cbc:URI',
    "2084": u'ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Si'
    u'gnature/@Id - No cumple con el estandar',
    "2085": u'El XML no contiene el tag ext:UBLExtensions/ext:UBLExtension/'
    u'ext:ExtensionContent/ds:Signature/@Id',
    "2086": u'ext:UBLExtensions/.../ds:Signature/ds:SignedInfo/ds:Canonical'
    u'izationMethod/@Algorithm - No cumple con el estandar',
    "2087": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignedInfo/ds:CanonicalizationMethod/@Algorithm',
    "2088": u'ext:UBLExtensions/.../ds:Signature/ds:SignedInfo/ds:Signature'
    u'Method/@Algorithm - No cumple con el estandar',
    "2089": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignedInfo/ds:SignatureMethod/@Algorithm',
    "2090": u'ext:UBLExtensions/.../ds:Signature/ds:SignedInfo/ds:Reference'
    u'/@URI - Debe estar vacio para id',
    "2091": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignedInfo/ds:Reference/@URI',
    "2092": u'ext:UBLExtensions/.../ds:Signature/ds:SignedInfo/.../ds:Trans'
    u'form@Algorithm - No cumple con el estandar',
    "2093": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignedInfo/ds:Reference/ds:Transform@Algorithm',
    "2094": u'ext:UBLExtensions/.../ds:Signature/ds:SignedInfo/ds:Reference'
    u'/ds:DigestMethod/@Algorithm - No cumple con el estandar',
    "2095": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignedInfo/ds:Reference/ds:DigestMethod/@Algorithm',
    "2096": u'ext:UBLExtensions/.../ds:Signature/ds:SignedInfo/ds:Reference'
    u'/ds:DigestValue - No  cumple con el estandar',
    "2097": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignedInfo/ds:Reference/ds:DigestValue',
    "2098": u'ext:UBLExtensions/.../ds:Signature/ds:SignatureValue - No cum'
    u'ple con el estandar',
    "2099": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:SignatureValue',
    "2100": u'ext:UBLExtensions/.../ds:Signature/ds:KeyInfo/ds:X509Data/ds:'
    u'X509Certificate - No cumple con el estandar',
    "2101": u'El XML no contiene el tag ext:UBLExtensions/.../ds:Signature/'
    u'ds:KeyInfo/ds:X509Data/ds:X509Certificate',
    "2102": u'Error al procesar la factura',
    "2103": u'La serie ingresada no es válida',
    "2104": u'Numero de RUC del emisor no existe',
    "2105": u'Factura a dar de baja no se encuentra registrada en SUNAT',
    "2106": u'Factura a dar de baja ya se encuentra en estado de baja',
    "2107": u'Numero de RUC SOL no coincide con RUC emisor',
    "2108": u'Presentacion fuera de fecha',
    "2109": u'El comprobante fue registrado previamente con otros datos',
    "2110": u'UBLVersionID - La versión del UBL no es correcta',
    "2111": u'El XML no contiene el tag o no existe informacion de UBLVersi'
    u'onID',
    "2112": u'CustomizationID - La version del documento no es correcta',
    "2113": u'El XML no contiene el tag o no existe informacion de Customiz'
    u'ationID',
    "2114": u'DocumentCurrencyCode -  El dato ingresado no cumple con la es'
    u'tructura',
    "2115": u'El XML no contiene el tag o no existe informacion de Document'
    u'CurrencyCode',
    "2116": u'El tipo de documento modificado por la Nota de credito debe s'
    u'er factura electronica o ticket',
    "2117": u'La serie o numero del documento modificado por la Nota de Cre'
    u'dito no cumple con el formato establecido',
    "2118": u'Debe indicar las facturas relacionadas a la Nota de Credito',
    "2119": u'La factura relacionada en la Nota de credito no esta registra'
    u'da.',
    "2120": u'La factura relacionada en la nota de credito se encuentra de '
    u'baja',
    "2121": u'La factura relacionada en la nota de credito esta registrada '
    u'como rechazada',
    "2122": u'El tag cac:LegalMonetaryTotal/cbc:PayableAmount debe tener in'
    u'formacion valida',
    "2123": u'RegistrationName -  El dato ingresado no cumple con el estandar',
    "2124": u'El XML no contiene el tag RegistrationName del emisor del doc'
    u'umento',
    "2125": u'ReferenceID -  El dato ingresado debe indicar SERIE-CORRELATI'
    u'VO del documento al que se relaciona la Nota',
    "2126": u'El XML no contiene informacion en el tag ReferenceID del docu'
    u'mento al que se relaciona la nota',
    "2127": u'ResponseCode -  El dato ingresado no cumple  con  la  estruct'
    u'ura',
    "2128": u'El XML no contiene el tag o no existe informacion de Response'
    u'Code',
    "2129": u'AdditionalAccountID -  El dato ingresado  en el tipo de docum'
    u'ento de identidad del receptor no cumple con el estandar',
    "2130": u'El XML no contiene el tag o no existe informacion de Addition'
    u'alAccountID del receptor del documento',
    "2131": u'CustomerAssignedAccountID - El numero de documento de identid'
    u'ad del receptor debe ser RUC',
    "2132": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del receptor del documento',
    "2133": u'RegistrationName -  El dato ingresado no cumple con el estandar',
    "2134": u'El XML no contiene el tag o no existe informacion de Registra'
    u'tionName del receptor del documento',
    "2135": u'cac:DiscrepancyResponse/cbc:Description - El dato ingresado n'
    u'o cumple con la estructura',
    "2136": u'El XML no contiene el tag o no existe informacion de cac:Disc'
    u'repancyResponse/cbc:Description',
    "2137": u'El Numero de orden del item no cumple con el formato establec'
    u'ido',
    "2138": u'CreditedQuantity/@unitCode - El dato ingresado no cumple con '
    u'el estandar',
    "2139": u'CreditedQuantity - El dato ingresado no cumple con el estandar',
    "2140": u'El PriceTypeCode debe tener el valor 01',
    "2141": u'cac:TaxCategory/cac:TaxScheme/cbc:ID - El dato ingresado no c'
    u'umple con el estandar',
    "2142": u'El codigo del tributo es invalido',
    "2143": u'cac:TaxScheme/cbc:Name del item - No existe el tag o el dato '
    u'ingresado no cumple con el estandar',
    "2144": u'cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode El dato ingresa'
    u'do no cumple con el estandar',
    "2145": u'El tipo de afectacion del IGV es incorrecto',
    "2146": u'El Nombre Internacional debe ser VAT',
    "2147": u'El sistema de calculo del ISC es incorrecto',
    "2148": u'El Nombre Internacional debe ser EXC',
    "2149": u'El dato ingresado en PayableAmount no cumple con el formato e'
    u'stablecido',
    "2150": u'El valor ingresado en AdditionalMonetaryTotal/cbc:ID es incor'
    u'recto',
    "2151": u'AdditionalMonetaryTotal/cbc:ID debe tener valor',
    "2152": u'Es obligatorio al menos un AdditionalInformation',
    "2153": u'Error al procesar la Nota de Credito',
    "2154": u'TaxAmount - El dato ingresado en impuestos globales no cumple'
    u' con el estandar',
    "2155": u'El XML no contiene el tag TaxAmount de impuestos globales',
    "2156": u'TaxScheme ID - El dato ingresado no cumple con el estandar',
    "2157": u'El codigo del tributo es invalido',
    "2158": u'El XML no contiene el tag o no existe informacion de TaxSchem'
    u'e ID de impuestos globales',
    "2159": u'TaxScheme Name - El dato ingresado no cumple con el estandar',
    "2160": u'El XML no contiene el tag o no existe informacion de TaxSchem'
    u'e Name de impuestos globales',
    "2161": u'CustomizationID - La version del documento no es correcta',
    "2162": u'El XML no contiene el tag o no existe informacion de Customiz'
    u'ationID',
    "2163": u'UBLVersionID - La versión del UBL no es correcta',
    "2164": u'El XML no contiene el tag o no existe informacion de UBLVersi'
    u'onID',
    "2165": u'Error al procesar la Nota de Debito',
    "2166": u'RegistrationName - El dato ingresado no cumple con el estandar',
    "2167": u'El XML no contiene el tag RegistrationName del emisor del doc'
    u'umento',
    "2168": u'DocumentCurrencyCode -  El dato ingresado no cumple con el fo'
    u'rmato establecido',
    "2169": u'El XML no contiene el tag o no existe informacion de Document'
    u'CurrencyCode',
    "2170": u'ReferenceID - El dato ingresado debe indicar SERIE-CORRELATIV'
    u'O del documento al que se relaciona la Nota',
    "2171": u'El XML no contiene informacion en el tag ReferenceID del docu'
    u'mento al que se relaciona la nota',
    "2172": u'ResponseCode - El dato ingresado no cumple con la estructura',
    "2173": u'El XML no contiene el tag o no existe informacion de Response'
    u'Code',
    "2174": u'cac:DiscrepancyResponse/cbc:Description - El dato ingresado n'
    u'o cumple con la estructura',
    "2175": u'El XML no contiene el tag o no existe informacion de cac:Disc'
    u'repancyResponse/cbc:Description',
    "2176": u'AdditionalAccountID -  El dato ingresado  en el tipo de docum'
    u'ento de identidad del receptor no cumple con el estandar',
    "2177": u'El XML no contiene el tag o no existe informacion de Addition'
    u'alAccountID del receptor del documento',
    "2178": u'CustomerAssignedAccountID - El numero de documento de identid'
    u'ad del receptor debe ser RUC.',
    "2179": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del receptor del documento',
    "2180": u'RegistrationName - El dato ingresado no cumple con el estandar',
    "2181": u'El XML no contiene el tag o no existe informacion de Registra'
    u'tionName del receptor del documento',
    "2182": u'TaxScheme ID - El dato ingresado no cumple con el estandar',
    "2183": u'El codigo del tributo es invalido',
    "2184": u'El XML no contiene el tag o no existe informacion de TaxSchem'
    u'e ID de impuestos globales',
    "2185": u'TaxScheme Name - El dato ingresado no cumple con el estandar',
    "2186": u'El XML no contiene el tag o no existe informacion de TaxSchem'
    u'e Name de impuestos globales',
    "2187": u'El Numero de orden del item no cumple con el formato establec'
    u'ido',
    "2188": u'DebitedQuantity/@unitCode El dato ingresado no cumple con el '
    u'estandar',
    "2189": u'DebitedQuantity El dato ingresado no cumple con el estandar',
    "2190": u'El XML no contiene el tag Price/cbc:PriceAmount en el detalle'
    u' de los Items',
    "2191": u'El XML no contiene el tag Price/cbc:LineExtensionAmount en el'
    u' detalle de los Items',
    "2192": u'EL PriceTypeCode debe tener el valor 01',
    "2193": u'cac:TaxCategory/cac:TaxScheme/cbc:ID El dato ingresado no cum'
    u'ple con el estandar',
    "2194": u'El codigo del tributo es invalido',
    "2195": u'cac:TaxScheme/cbc:Name del item - No existe el tag o el dato '
    u'ingresado no cumple con el estandar',
    "2196": u'cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode El dato ingresa'
    u'do no cumple con el estandar',
    "2197": u'El tipo de afectacion del IGV es incorrecto',
    "2198": u'El Nombre Internacional debe ser VAT',
    "2199": u'El sistema de calculo del ISC es incorrecto',
    "2200": u'El Nombre Internacional debe ser EXC',
    "2201": u'El tag cac:RequestedMonetaryTotal/cbc:PayableAmount debe tene'
    u'r informacion valida',
    "2202": u'TaxAmount - El dato ingresado en impuestos globales no cumple'
    u' con el estandar',
    "2203": u'El XML no contiene el tag TaxAmount de impuestos globales',
    "2204": u'El tipo de documento modificado por la Nota de Debito debe se'
    u'r factura electronica o ticket',
    "2205": u'La serie o numero del documento modificado por la Nota de Deb'
    u'ito no cumple con el formato establecido',
    "2206": u'Debe indicar los documentos afectados por la Nota de Debito',
    "2207": u'La factura relacionada en la nota de debito se encuentra de b'
    u'aja',
    "2208": u'La factura relacionada en la nota de debito esta registrada c'
    u'omo rechazada',
    "2209": u'La factura relacionada en la Nota de debito no esta registrada',
    "2210": u'El dato ingresado no cumple con el formato RC-fecha-correlativo',
    "2211": u'El XML no contiene el tag ID',
    "2212": u'UBLVersionID - La versión del UBL del resumen de boletas no e'
    u's correcta',
    "2213": u'El XML no contiene el tag UBLVersionID',
    "2214": u'CustomizationID - La versión del resumen de boletas no es cor'
    u'recta',
    "2215": u'El XML no contiene el tag CustomizationID',
    "2216": u'CustomerAssignedAccountID -  El dato ingresado no cumple con '
    u'el estandar',
    "2217": u'El XML no contiene el tag CustomerAssignedAccountID del emiso'
    u'r del documento',
    "2218": u'AdditionalAccountID - El dato ingresado no cumple con el esta'
    u'ndar',
    "2219": u'El XML no contiene el tag AdditionalAccountID del emisor del '
    u'documento',
    "2220": u'El ID debe coincidir con el nombre del archivo',
    "2221": u'El RUC debe coincidir con el RUC del nombre del archivo',
    "2222": u'El contribuyente no está autorizado a emitir comprobantes ele'
    u'ctronicos',
    "2223": u'El archivo ya fue presentado anteriormente',
    "2224": u'Numero de RUC SOL no coincide con RUC emisor',
    "2225": u'Numero de RUC del emisor no existe',
    "2226": u'El contribuyente no esta activo',
    "2227": u'El contribuyente no cumple con tipo de empresa o tributos req'
    u'ueridos',
    "2228": u'RegistrationName - El dato ingresado no cumple con el estanda'
    u'r',
    "2229": u'El XML no contiene el tag RegistrationName del emisor del doc'
    u'umento',
    "2230": u'IssueDate - El dato ingresado no cumple con el patron YYYY-MM'
    u'-DD',
    "2231": u'El XML no contiene el tag IssueDate',
    "2232": u'IssueDate- El dato ingresado no es valido',
    "2233": u'ReferenceDate - El dato ingresado no cumple con el patron YYY'
    u'Y-MM-DD',
    "2234": u'El XML no contiene el tag ReferenceDate',
    "2235": u'ReferenceDate- El dato ingresado no es valido',
    "2236": u'La fecha del IssueDate no debe ser mayor al Today',
    "2237": u'La fecha del ReferenceDate no debe ser mayor al Today',
    "2238": u'LineID - El dato ingresado no cumple con el estandar',
    "2239": u'LineID - El dato ingresado debe ser correlativo mayor a cero',
    "2240": u'El XML no contiene el tag LineID de SummaryDocumentsLine',
    "2241": u'DocumentTypeCode - El valor del tipo de documento es invalido',
    "2242": u'El XML no contiene el tag DocumentTypeCode',
    "2243": u'El dato ingresado  no cumple con el patron SERIE',
    "2244": u'El XML no contiene el tag DocumentSerialID',
    "2245": u'El dato ingresado en StartDocumentNumberID debe ser numerico',
    "2246": u'El XML no contiene el tag StartDocumentNumberID',
    "2247": u'El dato ingresado en sac:EndDocumentNumberID debe ser numerico',
    "2248": u'El XML no contiene el tag sac:EndDocumentNumberID',
    "2249": u'Los rangos deben ser mayores a cero',
    "2250": u'En el rango de comprobantes, el EndDocumentNumberID debe ser '
    u'mayor o igual al StartInvoiceNumberID',
    "2251": u'El dato ingresado en TotalAmount debe ser numerico mayor o ig'
    u'ual a cero',
    "2252": u'El XML no contiene el tag TotalAmount',
    "2253": u'El dato ingresado en TotalAmount debe ser numerico mayor a cero',
    "2254": u'PaidAmount - El dato ingresado no cumple con el estandar',
    "2255": u'El XML no contiene el tag PaidAmount',
    "2256": u'InstructionID - El dato ingresado no cumple con el estandar',
    "2257": u'El XML no contiene el tag InstructionID',
    "2258": u'Debe indicar Referencia de Importes asociados a las boletas d'
    u'e venta',
    "2259": u'Debe indicar 3 Referencias de Importes asociados a las boleta'
    u's de venta',
    "2260": u'PaidAmount - El dato ingresado debe ser mayor o igual a 0.00',
    "2261": u'cbc:Amount - El dato ingresado no cumple con el estandar',
    "2262": u'El XML no contiene el tag cbc:Amount',
    "2263": u'ChargeIndicator - El dato ingresado no cumple con el estandar',
    "2264": u'El XML no contiene el tag ChargeIndicator',
    "2265": u'Debe indicar Información acerca del Importe Total de Otros Ca'
    u'rgos',
    "2266": u'Debe indicar cargos mayores o iguales a cero',
    "2267": u'TaxScheme ID - El dato ingresado no cumple con el estandar',
    "2268": u'El codigo del tributo es invalido',
    "2269": u'El XML no contiene el tag TaxScheme ID de Información acerca '
    u'del importe total de un tipo particular de impuesto',
    "2270": u'TaxScheme Name - El dato ingresado no cumple con el estandar',
    "2271": u'El XML no contiene el tag TaxScheme Name de impuesto',
    "2272": u'TaxScheme TaxTypeCode - El dato ingresado no cumple con el es'
    u'tandar',
    "2273": u'TaxAmount - El dato ingresado no cumple con el estandar',
    "2274": u'El XML no contiene el tag TaxAmount',
    "2275": u'Si el codigo de tributo es 2000, el nombre del tributo debe s'
    u'er ISC',
    "2276": u'Si el codigo de tributo es 1000, el nombre del tributo debe s'
    u'er IGV',
    "2277": u'No se ha consignado ninguna informacion del importe total de '
    u'tributos',
    "2278": u'Debe indicar Información acerca del importe total de ISC e IGV',
    "2279": u'Debe indicar Items de consolidado de documentos',
    "2280": u'Existen problemas con la informacion del resumen de comproban'
    u'tes',
    "2281": u'Error en la validacion de los rangos de los comprobantes',
    "2282": u'Existe documento ya informado anteriormente',
    "2283": u'El dato ingresado no cumple con el formato RA-fecha-correlativo',
    "2284": u'El XML no contiene el tag ID',
    "2285": u'El ID debe coincidir  con el nombre del archivo',
    "2286": u'El RUC debe coincidir con el RUC del nombre del archivo',
    "2287": u'AdditionalAccountID - El dato ingresado no cumple con el esta'
    u'ndar',
    "2288": u'El XML no contiene el tag AdditionalAccountID del emisor del '
    u'documento',
    "2289": u'CustomerAssignedAccountID - El dato ingresado no cumple con e'
    u'l estandar',
    "2290": u'El XML no contiene el tag CustomerAssignedAccountID del emiso'
    u'r del documento',
    "2291": u'El contribuyente no esta autorizado a emitir comprobantes ele'
    u'ctronicos',
    "2292": u'Numero de RUC SOL no coincide con RUC emisor',
    "2293": u'Numero de RUC del emisor no existe',
    "2294": u'El contribuyente no esta activo',
    "2295": u'El contribuyente no cumple con tipo de empresa o tributos req'
    u'ueridos',
    "2296": u'RegistrationName - El dato ingresado no cumple con el estandar',
    "2297": u'El XML no contiene el tag RegistrationName del emisor del doc'
    u'umento',
    "2298": u'IssueDate - El dato ingresado no cumple con el patron YYYY-MM'
    u'-DD',
    "2299": u'El XML no contiene el tag IssueDate',
    "2300": u'IssueDate - El dato ingresado no es valido',
    "2301": u'La fecha del IssueDate no debe ser mayor al Today',
    "2302": u'ReferenceDate - El dato ingresado no cumple con el patron YYY'
    u'Y-MM-DD',
    "2303": u'El XML no contiene el tag ReferenceDate',
    "2304": u'ReferenceDate - El dato ingresado no es valido',
    "2305": u'LineID - El dato ingresado no cumple con el estandar',
    "2306": u'LineID - El dato ingresado debe ser correlativo mayor a cero',
    "2307": u'El XML no contiene el tag LineID de VoidedDocumentsLine',
    "2308": u'DocumentTypeCode - El valor del tipo de documento es invalido',
    "2309": u'El XML no contiene el tag DocumentTypeCode',
    "2310": u'El dato ingresado  no cumple con el patron SERIE',
    "2311": u'El XML no contiene el tag DocumentSerialID',
    "2312": u'El dato ingresado en DocumentNumberID debe ser numerico y com'
    u'o maximo de 8 digitos',
    "2313": u'El XML no contiene el tag DocumentNumberID',
    "2314": u'El dato ingresado en VoidReasonDescription debe contener info'
    u'rmación válida',
    "2315": u'El XML no contiene el tag VoidReasonDescription',
    "2316": u'Debe indicar Items en VoidedDocumentsLine',
    "2317": u'Error al procesar el resumen de anulados',
    "2318": u'CustomizationID - La version del documento no es correcta',
    "2319": u'El XML no contiene el tag CustomizationID',
    "2320": u'UBLVersionID - La version del UBL  no es la correcta',
    "2321": u'El XML no contiene el tag UBLVersionID',
    "2322": u'Error en la validacion de los rangos',
    "2323": u'Existe documento ya informado anteriormente en una comunicaci'
    u'on de baja',
    "2324": u'El archivo de comunicacion de baja ya fue presentado anterior'
    u'mente',
    "2325": u'El certificado usado no es el comunicado a SUNAT',
    "2326": u'El certificado usado se encuentra de baja',
    "2327": u'El certificado usado no se encuentra vigente',
    "2328": u'El certificado usado se encuentra revocado',
    "2329": u'La fecha de emision se encuentra fuera del limite permitido',
    "2330": u'La fecha de generación de la comunicación debe ser igual a la'
    u' fecha consignada en el nombre del archivo',
    "2331": u'Número de RUC del nombre del archivo no coincide con el consi'
    u'gnado en el contenido del archivo XML',
    "2332": u'Número de Serie del nombre del archivo no coincide con el con'
    u'signado en el contenido del archivo XML',
    "2333": u'Número de documento en el nombre del archivo no coincide con '
    u'el consignado en el contenido del XML',
    "2334": u'El documento electrónico ingresado ha sido alterado',
    "2335": u'El documento electrónico ingresado ha sido alterado',
    "2336": u'Ocurrió un error en el proceso de validación de la firma digi'
    u'tal',
    "2337": u'La moneda debe ser la misma en todo el documento',
    "2338": u'La moneda debe ser la misma en todo el documento',
    "2339": u'El dato ingresado en PayableAmount no cumple con el formato e'
    u'stablecido',
    "2340": u'El valor ingresado en AdditionalMonetaryTotal/cbc:ID es incor'
    u'recto',
    "2341": u'AdditionalMonetaryTotal/cbc:ID debe tener valor',
    "2342": u'Fecha de emision de la factura no coincide con la informada e'
    u'n la comunicacion',
    "2343": u'cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount - El dato ingresad'
    u'o no cumple con el estandar',
    "2344": u'El XML no contiene el tag cac:TaxTotal/cac:TaxSubtotal/cbc:Ta'
    u'xAmount',
    "2345": u'La serie no corresponde al tipo de comprobante',
    "2346": u'La fecha de generación del resumen debe ser igual a la fecha '
    u'consignada en el nombre del archivo',
    "2347": u'Los rangos informados en el archivo XML se encuentran duplica'
    u'dos o superpuestos',
    "2348": u'Los documentos informados en el archivo XML se encuentran dup'
    u'licados',
    "2349": u'Debe consignar solo un elemento sac:AdditionalMonetaryTotal c'
    u'on cbc:ID igual a 1001',
    "2350": u'Debe consignar solo un elemento sac:AdditionalMonetaryTotal c'
    u'on cbc:ID igual a 1002',
    "2351": u'Debe consignar solo un elemento sac:AdditionalMonetaryTotal c'
    u'on cbc:ID igual a 1003',
    "2352": u'Debe consignar solo un elemento cac:TaxTotal a nivel global p'
    u'ara IGV (cbc:ID igual a 1000)',
    "2353": u'Debe consignar solo un elemento cac:TaxTotal a nivel global p'
    u'ara ISC (cbc:ID igual a 2000)',
    "2354": u'Debe consignar solo un elemento cac:TaxTotal a nivel global p'
    u'ara Otros (cbc:ID igual a 9999)',
    "2355": u'Debe consignar solo un elemento cac:TaxTotal a nivel de item '
    u'para IGV (cbc:ID igual a 1000)',
    "2356": u'Debe consignar solo un elemento cac:TaxTotal a nivel de item '
    u'para ISC (cbc:ID igual a 2000)',
    "2357": u'Debe consignar solo un elemento sac:BillingPayment a nivel de'
    u' item con cbc:InstructionID igual a 01',
    "2358": u'Debe consignar solo un elemento sac:BillingPayment a nivel de'
    u' item con cbc:InstructionID igual a 02',
    "2359": u'Debe consignar solo un elemento sac:BillingPayment a nivel de'
    u' item con cbc:InstructionID igual a 03',
    "2360": u'Debe consignar solo un elemento sac:BillingPayment a nivel de'
    u' item con cbc:InstructionID igual a 04',
    "2361": u'Debe consignar solo un elemento cac:TaxTotal a nivel de item '
    u'para Otros (cbc:ID igual a 9999)',
    "2362": u'Debe consignar solo un tag cac:AccountingSupplierParty/cbc:Ad'
    u'ditionalAccountID',
    "2363": u'Debe consignar solo un tag cac:AccountingCustomerParty/cbc:Ad'
    u'ditionalAccountID',
    "2364": u'El comprobante contiene un tipo y número de Guía de Remisión '
    u'repetido',
    "2365": u'El comprobante contiene un tipo y número de Documento Relacio'
    u'nado repetido',
    "2366": u'El codigo en el tag sac:AdditionalProperty/cbc:ID debe tener '
    u'4 posiciones',
    "2367": u'El dato ingresado en PriceAmount del Precio de venta unitario'
    u' por item no cumple con el formato establecido',
    "2368": u'El dato ingresado en TaxSubtotal/cbc:TaxAmount del item no cu'
    u'mple con el formato establecido',
    "2369": u'El dato ingresado en PriceAmount del Valor de venta unitario '
    u'por item no cumple con el formato establecido',
    "2370": u'El dato ingresado en LineExtensionAmount del item no cumple c'
    u'on el formato establecido',
    "2371": u'El XML no contiene el tag cbc:TaxExemptionReasonCode de Afect'
    u'acion al IGV',
    "2372": u'El tag en el item cac:TaxTotal/cbc:TaxAmount debe tener el mi'
    u'smo valor que cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount',
    "2373": u'Si existe monto de ISC en el ITEM debe especificar el sistema'
    u' de calculo',
    "2374": u'La factura a dar de baja tiene una fecha de recepcion fuera d'
    u'el plazo permitido',
    "2375": u'Fecha de emision de la boleta no coincide con la fecha de emi'
    u'sion consignada en la comunicacion',
    "2376": u'La boleta de venta a dar de baja fue informada en un resumen '
    u'con fecha de recepcion fuera del plazo permitido',
    "2377": u'El Name o TaxTypeCode debe corresponder con el Id para el IGV',
    "2378": u'El Name o TaxTypeCode debe corresponder con el Id para el ISC',
    "2379": u'La numeracion de boleta de venta a dar de baja fue generada e'
    u'n una fecha fuera del plazo permitido',
    "2380": u'El documento tiene observaciones',
    "2381": u'Comprobante no cumple con el Grupo 1: No todos los items corr'
    u'esponden a operaciones gravadas a IGV',
    "2382": u'Comprobante no cumple con el Grupo 2: No todos los items corr'
    u'esponden a operaciones inafectas o exoneradas al IGV',
    "2383": u'Comprobante no cumple con el Grupo 3: Falta leyenda con codig'
    u'o 1002',
    "2384": u'Comprobante no cumple con el Grupo 3: Existe item con operaci'
    u'ón onerosa',
    "2385": u'Comprobante no cumple con el Grupo 4: Debe exitir Total descu'
    u'entos mayor a cero',
    "2386": u'Comprobante no cumple con el Grupo 5: Todos los items deben t'
    u'ener operaciones afectas a ISC',
    "2387": u'Comprobante no cumple con el Grupo 6: El monto de percepcion '
    u'no existe o es cero',
    "2388": u'Comprobante no cumple con el Grupo 6: Todos los items deben t'
    u'ener código de Afectación al IGV igual a 10',
    "2389": u'Comprobante no cumple con el Grupo 7: El codigo de moneda no '
    u'es diferente a PEN',
    "2390": u'Comprobante no cumple con el Grupo 8: No todos los items corr'
    u'esponden a operaciones gravadas a IGV',
    "2391": u'Comprobante no cumple con el Grupo 9: No todos los items corr'
    u'esponden a operaciones inafectas o exoneradas al IGV',
    "2392": u'Comprobante no cumple con el Grupo 10: Falta leyenda con codi'
    u'go 1002',
    "2393": u'Comprobante no cumple con el Grupo 10: Existe item con operac'
    u'ión onerosa',
    "2394": u'Comprobante no cumple con el Grupo 11: Debe existir Total des'
    u'cuentos mayor a cero',
    "2395": u'Comprobante no cumple con el Grupo 12: El codigo de moneda no'
    u' es diferente a PEN',
    "2396": u'Si el monto total es mayor a S/. 700.00 debe consignar tipo y'
    u' numero de documento del adquiriente',
    "2397": u'El tipo de documento del adquiriente no puede ser Numero de RUC',
    "2398": u'El documento a dar de baja se encuentra rechazado',
    "2399": u'El tipo de documento modificado por la Nota de credito debe s'
    u'er boleta electronica',
    "2400": u'El tipo de documento modificado por la Nota de debito debe se'
    u'r boleta electronica',
    "2401": u'No se puede leer (parsear) el archivo XML',
    "2402": u'El caso de prueba no existe',
    "2403": u'La numeracion o nombre del documento ya ha sido enviado anter'
    u'iormente',
    "2404": u'Documento afectado por la nota electronica no se encuentra au'
    u'torizado',
    "2405": u'Contribuyente no se encuentra autorizado como emisor de bolet'
    u'as electronicas',
    "2406": u'Existe mas de un tag sac:AdditionalMonetaryTotal con el mismo'
    u' ID',
    "2407": u'Existe mas de un tag sac:AdditionalProperty con el mismo ID',
    "2408": u'El dato ingresado en PriceAmount del Valor referencial unitar'
    u'io por item no cumple con el formato establecido',
    "2409": u'Existe mas de un tag cac:AlternativeConditionPrice con el mis'
    u'mo cbc:PriceTypeCode',
    "2410": u'Se ha consignado un valor invalido en el campo cbc:PriceTypeC'
    u'ode',
    "2411": u'Ha consignado mas de un elemento cac:AllowanceCharge con el m'
    u'ismo campo cbc:ChargeIndicator',
    "2412": u'Se ha consignado mas de un documento afectado por la nota (ta'
    u'g cac:BillingReference)',
    "2413": u'Se ha consignado mas de un motivo o sustento de la nota (tag '
    u'cac:DiscrepancyResponse/cbc:Description)',
    "2414": u'No se ha consignado en la nota el tag cac:DiscrepancyResponse',
    "2415": u'Se ha consignado en la nota mas de un tag cac:DiscrepancyResp'
    u'onse',
    "2416": u'Si existe leyenda Transferencia Gratuita debe consignar Total'
    u' Valor de Venta de Operaciones Gratuitas',
    "2417": u'Debe consignar Valor Referencial unitario por item en operaci'
    u'ones no onerosas',
    "2418": u'Si consigna Valor Referencial unitario por item en operacione'
    u's no onerosas,la operacion debe ser no onerosa.',
    "2419": u'El dato ingresado en AllowanceTotalAmount no cumple con el fo'
    u'rmato establecido',
    "2420": u'Ya transcurrieron mas de 25 dias calendarios para concluir co'
    u'n su proceso de homologacion',
    "2421": u'Debe indicar  toda la informacion de  sustento de translado d'
    u'e bienes.',
    "2422": u'El valor unitario debe ser menor al precio unitario.',
    "2423": u'Si ha consignado monto ISC a nivel de item, debe consignar un'
    u' monto a nivel de total.',
    "2424": u'RC Debe consignar solo un elemento sac:BillingPayment a nivel'
    u' de item con cbc:InstructionID igual a 05.',
    "2425": u'Si la  operacion es gratuita PriceTypeCode =02 y cbc:PriceAmo'
    u'unt> 0 el codigo de afectacion de igv debe ser  no onerosa es  dec'
    u'ir diferente de 10,20,30.',
    "2426": u'Documentos relacionados duplicados en el comprobante.',
    "2427": u'Solo debe de existir un tag AdditionalInformation.',
    "2428": u'Comprobante no cumple con grupo de facturas con detracciones.',
    "2429": u'Comprobante no cumple con grupo de facturas con comercio exte'
    u'rior.',
    "2430": u'Comprobante no cumple con grupo de facturas con tag de factur'
    u'a guia.',
    "2431": u'Comprobante no cumple con grupo de facturas con tags no tribu'
    u'tarios.',
    "2432": u'Comprobante no cumple con grupo de boletas con tags no tribut'
    u'arios.',
    "2433": u'Comprobante no cumple con grupo de facturas con tag venta iti'
    u'nerante.',
    "2434": u'Comprobante no cumple con grupo de boletas con tag venta itin'
    u'erante.',
    "2435": u'Comprobante no cumple con grupo de boletas con ISC.',
    "2436": u'Comprobante no cumple con el grupo de boletas de venta con pe'
    u'rcepcion: El monto de percepcion no existe o es cero.',
    "2437": u'Comprobante no cumple con el grupo de boletas de venta con pe'
    u'rcepcion: Todos los items deben tener código de Afectación al IGV '
    u'igual a 10.',
    "2438": u'Comprobante no cumple con grupo de facturas con tag venta ant'
    u'icipada I.',
    "2439": u'Comprobante no cumple con grupo de facturas con tag venta ant'
    u'icipada II.',
    "2500": u'Ingresar descripción y valor venta por ítem para documento de'
    u' anticipos.',
    "2501": u'Valor venta debe ser mayor a cero.',
    "2502": u'Los valores totales deben ser mayores a cero.',
    "2503": u'PaidAmount: monto anticipado por documento debe ser mayor a c'
    u'ero.',
    "2504": u'Falta referencia de la factura relacionada con anticipo.',
    "2505": u'cac:PrepaidPayment/cbc:ID/@SchemaID: Código de referencia deb'
    u'e ser 02 o 03.',
    "2506": u'cac:PrepaidPayment/cbc:ID: Factura o boleta no existe o comun'
    u'icada de Baja.',
    "2507": u'Factura relacionada con anticipo no corresponde como factura '
    u'de anticipo.',
    "2508": u'Ingresar documentos por anticipos.',
    "2509": u'Total de anticipos diferente a los montos anticipados por doc'
    u'umento.',
    "2510": u'Nro nombre del documento no tiene el formato correcto.',
    "2511": u'El tipo de documento no es aceptado.',
    "2512": u'No existe información de serie o número.',
    "2513": u'Dato no cumple con formato de acuerdo al número de comprobante.',
    "2514": u'No existe información de receptor de documento.',
    "2515": u'Dato ingresado no cumple con catalogo 6.',
    "2516": u'Debe indicar tipo de documento.',
    "2517": u'Dato no cumple con formato establecido.',
    "2518": u'Calculo IGV no es correcto.',
    "2519": u'El importe total no coincide con la sumatoria de los valores '
    u'de venta mas los tributos mas los cargos.',
    "2520": u'cac:PrepaidPayment/cbc:InstructionID/@SchemaID – El tipo docu'
    u'mento debe ser 6 del catalogo de tipo de documento.',
    "2521": u'cac:PrepaidPayment/cbc:ID - El dato ingresado debe indicar SE'
    u'RIE-CORRELATIVO del documento que se realizo el anticipo.',
    "2522": u'No existe información del documento del anticipo.',
    "2523": u'GrossWeightMeasure – El dato ingresado no cumple con el forma'
    u'to establecido.',
    "2524": u'El dato ingresado en Amount no cumple con el formato establec'
    u'ido.',
    "2525": u'El dato ingresado en Quantity no cumple con el formato establ'
    u'ecido.',
    "2526": u'El dato ingresado en Percent no cumple con el formato estable'
    u'cido.',
    "2527": u'PrepaidAmount: Monto total anticipado debe ser mayor a cero.',
    "2528": u'cac:OriginatorDocumentReference/cbc:ID/@SchemaID – El tipo do'
    u'cumento debe ser 6 del catalogo de tipo de documento.',
    "2529": u'RUC que emitio documento de anticipo, no existe.',
    "2530": u'RUC que solicita la emision de la factura, no existe. ',
    "2531": u'Codigo del Local Anexo del emisor no existe.',
    "2532": u'No existe información de modalidad de transporte.',
    "2533": u'Si ha consignado Transporte Privado, debe consignar Licencia '
    u'de conducir, Placa, N constancia de inscripcion y marca del vehicu'
    u'lo.',
    "2534": u'Si ha consignado Transporte púbico, debe consignar Datos del '
    u'transportista.',
    "2535": u'La nota de crédito por otros conceptos tributarios debe tener'
    u' Otros Documentos Relacionados.',
    "2536": u'Serie y numero no se encuentra registrado como baja por cambi'
    u'o de destinatario.',
    "2537": u'cac:OrderReference/cac:DocumentReference/cbc:DocumentTypeCode'
    u' - El tipo de documento de serie y número dado de baja es incorrec'
    u'ta.',
    "2538": u'El contribuyente no se encuentra autorizado como emisor elect'
    u'ronico de Guía o de factura o de boletaFactura GEM.',
    "2539": u'El contribuyente no esta activo.',
    "2540": u'El contribuyente no esta habido.',
    "2541": u'El XML no contiene el tag o no existe informacion del tipo de'
    u' documento identidad del remitente.',
    "2542": u'cac:DespatchSupplierParty/cbc:CustomerAssignedAccountID@schem'
    u'eID - El valor ingresado como tipo de documento identidad del remi'
    u'tente es incorrecta.',
    "2543": u'El XML no contiene el tag o no existe informacion de la direc'
    u'ción completa y detallada en domicilio fiscal.',
    "2544": u'El XML no contiene el tag o no existe información de la provi'
    u'ncia en domicilio fiscal.',
    "2545": u'El XML no contiene el tag o no existe información del departa'
    u'mento en domicilio fiscal.',
    "2546": u'El XML no contiene el tag o no existe información del distrit'
    u'o en domicilio fiscal.',
    "2547": u'El XML no contiene el tag o no existe información del país en'
    u' domicilio fiscal.',
    "2548": u'El valor del país inválido.',
    "2549": u'El XML no contiene el tag o no existe informacion del tipo de'
    u' documento identidad del destinatario.',
    "2550": u'cac:DeliveryCustomerParty/cbc:CustomerAssignedAccountID@schem'
    u'eID - El dato ingresado de tipo de documento identidad del destina'
    u'tario no cumple con el estandar.',
    "2551": u'El XML no contiene el tag o no existe informacion de Customer'
    u'AssignedAccountID del proveedor de servicios.',
    "2552": u'El XML no contiene el tag o no existe informacion del tipo de'
    u' documento identidad del proveedor.',
    "2553": u'cac:SellerSupplierParty/cbc:CustomerAssignedAccountID@schemeI'
    u'D - El dato ingresado no es valido.',
    "2554": u'Para el motivo de traslado ingresado el Destinatario debe ser'
    u' igual al remitente.',
    "2555": u'Destinatario no debe ser igual al remitente.',
    "2556": u'cbc:TransportModeCode -  dato ingresado no es valido.',
    "2557": u'La fecha del StartDate no debe ser menor al Today.',
    "2558": u'El XML no contiene el tag o no existe informacion en Numero d'
    u'e Ruc del transportista.',
    "2559": u'/DespatchAdvice/cac:Shipment/cac:ShipmentStage/cac:CarrierPar'
    u'ty/cac:PartyIdentification/cbc:ID  - El dato ingresado no cumple c'
    u'on el formato establecido.',
    "2560": u'Transportista  no debe ser igual al remitente o destinatario.',
    "2561": u'El XML no contiene el tag o no existe informacion del tipo de'
    u' documento identidad del transportista.',
    "2562": u'/DespatchAdvice/cac:Shipment/cac:ShipmentStage/cac:CarrierPar'
    u'ty/cac:PartyIdentification/cbc:ID@schemeID  - El dato ingresado no'
    u' es valido.',
    "2563": u'El XML no contiene el tag o no existe informacion de Apellido'
    u', Nombre o razon social del transportista.',
    "2564": u'Razon social transportista - El dato ingresado no cumple con '
    u'el formato establecido.',
    "2565": u'El XML no contiene el tag o no existe informacion del tipo de'
    u' unidad de transporte.',
    "2566": u'El XML no contiene el tag o no existe informacion del Numero '
    u'de placa del vehículo.',
    "2567": u'Numero de placa del vehículo - El dato ingresado no cumple co'
    u'n el formato establecido.',
    "2568": u'El XML no contiene el tag o no existe informacion en el Numer'
    u'o de documento de identidad del conductor.',
    "2569": u'Documento identidad del conductor - El dato ingresado no cump'
    u'le con el formato establecido.',
    "2570": u'El XML no contiene el tag o no existe informacion del tipo de'
    u' documento identidad del conductor.',
    "2571": u'cac:DriverPerson/ID@schemeID - El valor ingresado de tipo de '
    u'documento identidad de conductor es incorrecto.',
    "2572": u'El XML no contiene el tag o no existe informacion del Numero '
    u'de licencia del conductor.',
    "2573": u'Numero de licencia del conductor - El dato ingresado no cumpl'
    u'e con el formato establecido.',
    "2574": u'El XML no contiene el tag o no existe informacion de direccio'
    u'n detallada de punto de llegada.',
    "2575": u'El XML no contiene el tag o no existe informacion de CityName.',
    "2576": u'El XML no contiene el tag o no existe informacion de District.',
    "2577": u'El XML no contiene el tag o no existe informacion de direccio'
    u'n detallada de punto de partida.',
    "2578": u'El XML no contiene el tag o no existe informacion de CityName.',
    "2579": u'El XML no contiene el tag o no existe informacion de District.',
    "2580": u'El XML No contiene el tag o no existe información de la canti'
    u'dad del item.',
    "2600": u'El comprobante fue enviado fuera del plazo permitido.',
    "2601": u'Señor contribuyente a la fecha no se encuentra registrado ó h'
    u'abilitado con la condición de Agente de percepción.',
    "2602": u'El régimen percepción enviado no corresponde con su condición'
    u' de Agente de percepción.',
    "2603": u'La tasa de percepción enviada no corresponde con el régimen d'
    u'e percepción.',
    "2604": u'El Cliente no puede ser el mismo que el Emisor del comprobant'
    u'e de percepción.',
    "2605": u'Número de RUC del Cliente no existe.',
    "2606": u'Documento de identidad del Cliente no existe.',
    "2607": u'La moneda del importe de cobro debe ser la misma que la del d'
    u'ocumento relacionado.',
    "2608": u'Los montos de pago, percibidos y montos cobrados consignados '
    u'para el documento relacionado no son correctos.',
    "2609": u'El comprobante electrónico enviado no se encuentra registrado'
    u' en la SUNAT.',
    "2610": u'La fecha de emisión, Importe total del comprobante y la moned'
    u'a del comprobante electrónico enviado no son los registrados en lo'
    u's Sistemas de SUNAT.',
    "2611": u'El comprobante electrónico no ha sido emitido al cliente.',
    "2612": u'La fecha de cobro debe estar entre el primer día calendario d'
    u'el mes al cual corresponde la fecha de emisión del comprobante de '
    u'percepción o desde la fecha de emisión del comprobante relacionado.',
    "2613": u'El Nro. de documento con número de cobro ya se encuentra en l'
    u'a Relación de Documentos Relacionados agregados.',
    "2614": u'El Nro. de documento con el número de cobro ya se encuentra r'
    u'egistrado como pago realizado.',
    "2615": u'Importe total percibido debe ser igual a la suma de los impor'
    u'tes percibidos por cada documento relacionado.',
    "2616": u'Importe total cobrado debe ser igual a la suma de los importe'
    u' totales cobrados por cada documento relacionado.',
    "2617": u'Señor contribuyente a la fecha no se encuentra registrado ó h'
    u'abilitado con la condición de Agente de retención.',
    "2618": u'El régimen retención enviado no corresponde con su condición '
    u'de Agente de retención.',
    "2619": u'La tasa de retención enviada no corresponde con el régimen de'
    u' retención.',
    "2620": u'El Proveedor no puede ser el mismo que el Emisor del comproba'
    u'nte de retención.',
    "2621": u'Número de RUC del Proveedor no existe.',
    "2622": u'La moneda del importe de pago debe ser la misma que la del do'
    u'cumento relacionado.',
    "2623": u'Los montos de pago, retenidos y montos pagados consignados pa'
    u'ra el documento relacionado no son correctos.',
    "2624": u'El comprobante electrónico no ha sido emitido por el proveedor.',
    "2625": u'La fecha de pago debe estar entre el primer día calendario de'
    u'l mes al cual corresponde la fecha de emisión del comprobante de r'
    u'etención o desde la fecha de emisión del comprobante relacionado.',
    "2626": u'El Nro. de documento con el número de pago ya se encuentra en'
    u' la Relación de Documentos Relacionados agregados.',
    "2627": u'El Nro. de documento con el número de pago ya se encuentra re'
    u'gistrado como pago realizado.',
    "2628": u'Importe total retenido debe ser igual a la suma de los import'
    u'es retenidos por cada documento relacionado.',
    "2629": u'Importe total pagado debe ser igual a la suma de los importes'
    u' pagados por cada documento relacionado.',
    "2630": u'La serie o numero del documento(01) modificado por la Nota de'
    u' Credito no cumple con el formato establecido para tipo codigo Not'
    u'a Credito 10.',
    "2631": u'La serie o numero del documento(12) modificado por la Nota de'
    u' Credito no cumple con el formato establecido para tipo codigo Not'
    u'a Credito 10.',
    "2632": u'La serie o numero del documento(56) modificado por la Nota de'
    u' Credito no cumple con el formato establecido para tipo codigo Not'
    u'a Credito 10.',
    "2633": u'La serie o numero del documento(03) modificado por la Nota de'
    u' Credito no cumple con el formato establecido para tipo codigo Not'
    u'a Credito 10.',
    "2634": u'ReferenceID - El dato ingresado debe indicar serie correcta d'
    u'el documento al que se relaciona la Nota tipo 10.',
    "2635": u'Debe existir DocumentTypeCode de Otros documentos relacionado'
    u's con valor 99 para un tipo codigo Nota Credito 10.',
    "2636": u'No existe datos del ID de los documentos relacionados con val'
    u'or 99 para un tipo codigo Nota Credito 10.',
    "2637": u'No existe datos del DocumentType de los documentos relacionad'
    u'os con valor 99 para un tipo codigo Nota Credito 10.',
    "2640": u'Operacion gratuita, solo debe consignar un monto referencial',
    "2641": u'Operacion gratuita,  debe consignar Total valor venta - opera'
    u'ciones gratuitas  mayor a cero',
    "2642": u'Operaciones de exportacion, deben consignar Tipo Afectacion i'
    u'gual a 40',
    "2643": u'Factura de operacion sujeta IVAP debe consignar Monto de impu'
    u'estos por item',
    "2644": u'Factura de operacion sujeta IVAP solo debe tener ítems con có'
    u'digo afectación IGV 17.',
    "2645": u'Factura de operacion sujeta a IVAP debe consignar items con c'
    u'odigo de tributo 1000',
    "2646": u'Factura de operacion sujeta a IVAP debe consignar  items con '
    u'nombre  de tributo IVAP',
    "2647": u'Código tributo  UN/ECE debe ser VAT',
    "2648": u'Factura de operacion sujeta al IVAP, solo puede consignar inf'
    u'ormacion para operacion gravadas',
    "2649": u'Operación sujeta al IVAP, debe consignar monto en total opera'
    u'ciones gravadas ',
    "2650": u'Factura de operacion sujeta al IVAP , no debe consignar valor'
    u' para ISC o debe ser 0',
    "2651": u'Factura de operacion sujeta al IVAP , no debe consignar valor'
    u' para IGV o debe ser 0',
    "2652": u'Factura de operacion sujeta al IVAP , debe registrar mensaje '
    u'2007',
    "2653": u'Servicios prestados No domiciliados. Total IGV debe se mayor '
    u'a cero',
    "2654": u'Servicios prestados No domiciliados. Código tributo a consign'
    u'ar debe ser 1000',
    "2655": u'Servicios prestados No domiciliados. El código de afectación '
    u'debe ser 40',
    "2656": u'Servicios prestados No domiciliados. Código tributo  UN/ECE d'
    u'ebe ser VAT',
    "2657": u'El Nro. de documento ya fué utilizado en la emision de CPE.',
    "2658": u'El Nro. de documento no se ha informado o no se encuentra en '
    u'estado Revertido',
    "2659": u'La fecha de cobro de cada documento relacionado deben ser del'
    u' mismo Periodo (mm/aaaa), asimismo estas fechas podrán ser menores'
    u' o iguales a la fecha de emisión del comprobante de percepción',
    "2660": u'Los datos del CPE revertido no corresponden a los registrados'
    u' en la SUNAT',
    "2661": u'La fecha de cobro de cada documento relacionado deben ser del'
    u' mismo Periodo (mm/aaaa), asimismo estas fechas podrán ser menores'
    u' o iguales a la fecha de emisión del comprobante de retencion',
    "2662": u'El Nro. de documento ya fué utilizado en la emision de CRE.',
    "2663": u'El documento indicado no existe no puede ser modificado/elimi'
    u'nado',
    "2664": u'El calculo de la base imponible de percepción y el monto de l'
    u'a percepción no coincide con el monto total informado.',
    "2665": u'El contribuyente no se encuentra autorizado a emitir Tickets',
    "2666": u'Las percepciones son solo válidas para boletas de venta al co'
    u'ntado.',
    "2667": u'Importe total percibido debe ser igual a la suma de los impor'
    u'tes percibidos por cada documento relacionado.',
    "2668": u'Importe total cobrado debe ser igual a la suma de los importe'
    u's cobrados por cada documento relacionado.',
    "2669": u'El dato ingresado en TotalInvoiceAmount debe ser numérico may'
    u'or a cero',
    "2670": u'La razón social no corresponde al ruc informado.',
    "2671": u'La fecha de generación de la comunicación debe ser mayor o ig'
    u'ual a la fecha de generación del documento revertido.',
    "2672": u'La fecha de generación del documento revertido debe ser menor'
    u' o igual a la fecha actual.',
    "2673": u'El dato ingresado no cumple con el formato RR-fecha-correlati'
    u'vo.',
    "2674": u'El dato ingresado  no cumple con el formato de DocumentSerial'
    u'ID, para DocumentTypeCode con valor 20.',
    "2675": u'El dato ingresado  no cumple con el formato de DocumentSerial'
    u'ID, para DocumentTypeCode con valor 40.',
    "2676": u'El XML no contiene el tag o no existe información del número '
    u'de RUC del emisor',
    "2677": u'El valor ingresado como número de RUC del emisor es incorrecto',
    "2678": u'El XML no contiene el atributo o no existe información del ti'
    u'po de documento del emisor',
    "2679": u'El XML no contiene el tag o no existe información del número '
    u'de documento de identidad del cliente',
    "2680": u'El valor ingresado como documento de identidad del cliente es'
    u' incorrecto',
    "2681": u'El XML no contiene el atributo o no existe información del ti'
    u'po de documento del cliente',
    "2682": u'El valor ingresado como tipo de documento del cliente es inco'
    u'rrecto',
    "2683": u'El XML no contiene el tag o no existe información del Importe'
    u' total Percibido',
    "2684": u'El XML no contiene el tag o no existe información de la moned'
    u'a del Importe total Percibido',
    "2685": u'El valor de la moneda del Importe total Percibido debe ser PEN',
    "2686": u'El XML no contiene el tag o no existe información del Importe'
    u' total Cobrado',
    "2687": u'El dato ingresado en SUNATTotalCashed debe ser numérico mayor'
    u' a cero',
    "2689": u'El XML no contiene el tag o no existe información de la moned'
    u'a del Importe total Cobrado',
    "2690": u'El valor de la moneda del Importe total Cobrado debe ser PEN',
    "2691": u'El XML no contiene el tag o no existe información del tipo de'
    u' documento relacionado',
    "2692": u'El tipo de documento relacionado no es válido',
    "2693": u'El XML no contiene el tag o no existe información del número '
    u'de documento relacionado',
    "2694": u'El número de documento relacionado no está permitido o no es '
    u'valido',
    "2695": u'El XML no contiene el tag o no existe información del Importe'
    u' total documento Relacionado',
    "2696": u'El dato ingresado en el importe total documento relacionado d'
    u'ebe ser numérico mayor a cero',
    "2697": u'El XML no contiene el tag o no existe información del número '
    u'de cobro',
    "2698": u'El dato ingresado en el número de cobro no es válido',
    "2699": u'El XML no contiene el tag o no existe información del Importe'
    u' del cobro',
    "2700": u'El dato ingresado en el Importe del cobro debe ser numérico m'
    u'ayor a cero',
    "2701": u'El XML no contiene el tag o no existe información de la moned'
    u'a del documento Relacionado',
    "2702": u'El XML no contiene el tag o no existe información de la fecha'
    u' de cobro del documento Relacionado',
    "2703": u'La fecha de cobro del documento relacionado no es válido',
    "2704": u'El XML no contiene el tag o no existe información del Importe'
    u' percibido',
    "2705": u'El dato ingresado en el Importe percibido debe ser numérico m'
    u'ayor a cero',
    "2706": u'El XML no contiene el tag o no existe información de la moned'
    u'a de importe percibido',
    "2707": u'El valor de la moneda de importe percibido debe ser PEN',
    "2708": u'El XML no contiene el tag o no existe información de la Fecha'
    u' de Percepción',
    "2709": u'La fecha de percepción no es válido',
    "2710": u'El XML no contiene el tag o no existe información del Monto t'
    u'otal a cobrar',
    "2711": u'El dato ingresado en el Monto total a cobrar debe ser numéric'
    u'o mayor a cero',
    "2712": u'El XML no contiene el tag o no existe información de la moned'
    u'a del Monto total a cobrar',
    "2713": u'El valor de la moneda del Monto total a cobrar debe ser PEN',
    "2714": u'El valor de la moneda de referencia para el tipo de cambio no'
    u' es válido',
    "2715": u'El valor de la moneda objetivo para la Tasa de Cambio debe se'
    u'r PEN',
    "2716": u'El dato ingresado en el tipo de cambio debe ser numérico mayo'
    u'r a cero',
    "2717": u'La fecha de cambio no es válido',
    "2718": u'El valor de la moneda del documento Relacionado no es válido',
    "2719": u'El XML no contiene el tag o no existe información de la moned'
    u'a de referencia para el tipo de cambio',
    "2720": u'El XML no contiene el tag o no existe información de la moned'
    u'a objetivo para la Tasa de Cambio',
    "2721": u'El XML no contiene el tag o no existe información del tipo de'
    u' cambio',
    "2722": u'El XML no contiene el tag o no existe información de la fecha'
    u' de cambio',
    "2723": u'El XML no contiene el tag o no existe información del número '
    u'de documento de identidad del proveedor',
    "2724": u'El valor ingresado como documento de identidad del proveedor '
    u'es incorrecto',
    "2725": u'El XML no contiene el tag o no existe información del Importe'
    u' total Retenido',
    "2726": u'El XML no contiene el tag o no existe información de la moned'
    u'a del Importe total Retenido',
    "2727": u'El XML no contiene el tag o no existe información de la moned'
    u'a del Importe total Retenido',
    "2728": u'El valor de la moneda del Importe total Retenido debe ser PEN',
    "2729": u'El XML no contiene el tag o no existe información del Importe'
    u' total Pagado',
    "2730": u'El dato ingresado en SUNATTotalPaid debe ser numérico mayor a'
    u' cero',
    "2731": u'El XML no contiene el tag o no existe información de la moned'
    u'a del Importe total Pagado',
    "2732": u'El valor de la moneda del Importe total Pagado debe ser PEN',
    "2733": u'El XML no contiene el tag o no existe información del número '
    u'de pago',
    "2734": u'El dato ingresado en el número de pago no es válido',
    "2735": u'El XML no contiene el tag o no existe información del Importe'
    u' del pago',
    "2736": u'El dato ingresado en el Importe del pago debe ser numérico ma'
    u'yor a cero',
    "2737": u'El XML no contiene el tag o no existe información de la fecha'
    u' de pago del documento Relacionado',
    "2738": u'La fecha de pago del documento relacionado no es válido',
    "2739": u'El XML no contiene el tag o no existe información del Importe'
    u' retenido',
    "2740": u'El dato ingresado en el Importe retenido debe ser numérico ma'
    u'yor a cero',
    "2741": u'El XML no contiene el tag o no existe información de la moned'
    u'a de importe retenido',
    "2742": u'El valor de la moneda de importe retenido debe ser PEN',
    "2743": u'El XML no contiene el tag o no existe información de la Fecha'
    u' de Retención',
    "2744": u'La fecha de retención no es válido',
    "2745": u'El XML no contiene el tag o no existe información del Importe'
    u' total a pagar (neto)',
    "2746": u'El dato ingresado en el Importe total a pagar (neto) debe ser'
    u' numérico mayor a cero',
    "2747": u'El XML no contiene el tag o no existe información de la Moned'
    u'a del monto neto pagado',
    "2748": u'El valor de la Moneda del monto neto pagado debe ser PEN',
    "2749": u'La moneda de referencia para el tipo de cambio debe ser la mi'
    u'sma que la del documento relacionado',
    "2750": u'El comprobante que desea revertir no existe.',
    "2751": u'El comprobante fue informado previamente en una reversión.',
    "2752": u'El número de ítem no puede estar duplicado.',
    "2753": u'No debe existir mas de una referencia en guía dada de baja.',
    "2754": u'El tipo de documento de la guia dada de baja es incorrecto (t'
    u'ipo documento = 09).',
    "2755": u'El tipo de documento relacionado es incorrecto (ver catalogo '
    u'nro 21).',
    "2756": u'El numero de documento relacionado no cumple con el estandar.',
    "2757": u'El XML no contiene el tag o no existe información del número '
    u'de documento de identidad del destinatario.',
    "2758": u'El valor ingresado como numero de documento de identidad del '
    u'destinatario no cumple con el estandar.',
    "2759": u'El XML no contiene el atributo o no existe información del ti'
    u'po de documento del destinatario.',
    "2760": u'El valor ingresado como tipo de documento del destinatario es'
    u' incorrecto.',
    "2761": u'El XML no contiene el atributo o no existe información del no'
    u'mbre o razon social del destinatario.',
    "2762": u'El valor ingresado como tipo de documento del nombre o razon '
    u'social del destinatario es incorrecto.',
    "2763": u'El XML no contiene el tag o no existe información del número '
    u'de documento de identidad del tercero relacionado.',
    "2764": u'El valor ingresado como numero de documento de identidad del '
    u'tercero relacionado no cumple con el estandar.',
    "2765": u'El XML no contiene el atributo o no existe información del ti'
    u'po de documento del tercero relacionado.',
    "2766": u'El valor ingresado como tipo de documento del tercero relacio'
    u'nado es incorrecto.',
    "2767": u'Para importación, el XML no contiene el tag o no existe infor'
    u'macion del numero de DAM.',
    "2768": u'Para importación, el XML no contiene el tag o no existe infor'
    u'macion del numero de manifiesto de carga.',
    "2769": u'El valor ingresado como numero de DAM no cumple con el estand'
    u'ar.',
    "2770": u'El valor ingresado como numero de manifiesto de carga no cump'
    u'le con el estandar.',
    "2771": u'El XML no contiene el atributo o no existe informacion en num'
    u'ero de bultos o pallets obligatorio para importación.',
    "2772": u'El valor ingresado como numero de bultos o pallets no cumple '
    u'con el estandar.',
    "2773": u'El valor ingresado como modalidad de transporte no es correcto.',
    "2774": u'El XML no contiene datos de vehiculo o datos de conductores p'
    u'ara una operación de transporte publico completo.',
    "2775": u'El XML no contiene el atributo o no existe informacion del co'
    u'digo de ubigeo.',
    "2776": u'El valor ingresado como codigo de ubigeo no cumple con el est'
    u'andar.',
    "2777": u'El XML no contiene el atributo o no existe informacion de dir'
    u'eccion completa y detallada.',
    "2778": u'El valor ingresado como direccion completa y detallada no cum'
    u'ple con el estandar.',
    "2779": u'El XML no contiene el atributo o no existe informacion de can'
    u'tida de items',
    "2780": u'El valor ingresado en cantidad de items no cumple con el esta'
    u'ndar',
    "2781": u'El XML no contiene el atributo o no existe informacion de des'
    u'cripcion del items',
    "2782": u'El valor ingresado en descripcion del items no cumple con el '
    u'estandar',
    "2783": u'El valor ingresado en codigo del item no cumple con el estand'
    u'ar.',
    "2784": u'Debe consignar codigo de regimen de percepcion (sac:Additiona'
    u'lMonetaryTotal/cbc:ID@schemeID).',
    "2785": u'sac:ReferenceAmount es obligatorio y mayor a cero cuando sac:'
    u'AdditionalMonetaryTotal/cbc:ID es 2001',
    "2786": u'El dato ingresado en sac:ReferenceAmount no cumple con el for'
    u'mato establecido',
    "2787": u'Debe consignar la moneda para la Base imponible percepcion (s'
    u'ac:ReferenceAmount/@currencyID)',
    "2788": u'El dato ingresado en sac:ReferenceAmount/@currencyID debe ser'
    u' PEN',
    "2789": u'cbc:PayableAmount es obligatorio y mayor a cero cuando sac:Ad'
    u'ditionalMonetaryTotal/cbc:ID es 2001',
    "2790": u'El dato ingresado en cbc:PayableAmount no cumple con el forma'
    u'to establecido',
    "2791": u'Debe consignar la moneda para el Monto de la percepcion (cbc:'
    u'PayableAmount/@currencyID)',
    "2792": u'El dato ingresado en cbc:PayableAmount/@currencyID debe ser PEN',
    "2793": u'sac:TotalAmount es obligatorio y mayor a cero cuando sac:Addi'
    u'tionalMonetaryTotal/cbc:ID es 2001',
    "2794": u'El dato ingresado en sac:TotalAmount no cumple con el formato'
    u' establecido',
    "2795": u'Debe consignar la moneda para el Monto Total incluido la perc'
    u'epcion (sac:TotalAmount/@currencyID)',
    "2796": u'El dato ingresado en sac:TotalAmount/@currencyID debe ser PEN',
    "2797": u'sac:ReferenceAmount no puede ser mayor al importe total de la'
    u' venta (cac:LegalMonetaryTotal/cbc:PayableAmount) cuando sac:Addit'
    u'ionalMonetaryTotal/cbc:ID es 2001',
    "2798": u'cbc:PayableAmount no tiene el valor correcto cuando sac:Addit'
    u'ionalMonetaryTotal/cbc:ID es 2001',
    "2799": u'sac:TotalAmount no tiene el valor correcto cuando sac:Additio'
    u'nalMonetaryTotal/cbc:ID es 2001',
    "2800": u'AdditionalAccountID -  El dato ingresado  en el tipo de docum'
    u'ento de identidad del receptor no esta permitido.',
    "2801": u'CustomerAssignedAccountID -  El DNI ingresado no cumple con e'
    u'l estandar.',
    "2802": u'CustomerAssignedAccountID -  El RUC ingresado no cumple con e'
    u'l estandar.',
    "2803": u'ID - No cumple con el formato UUID',
    "2804": u'La fecha de recepcion del comprobante por ose, no debe de ser'
    u' mayor a la fecha de recepcion de sunat',
    "2805": u'El XML no contiene el tag IssueTime',
    "2806": u'IssueTime - El dato ingresado  no cumple con el patrón hh:mm:'
    u'ss.sssss',
    "2807": u'El XML no contiene el tag ResponseDate',
    "2808": u'ResponseDate - El dato ingresado  no cumple con el patrón YYY'
    u'Y-MM-DD',
    "2809": u'La fecha de recepcion del comprobante por ose, no debe de ser'
    u' mayor a la fecha de comprobacion del ose',
    "2810": u'La fecha de comprobacion del comprobante en OSE no puede ser '
    u'mayor a la fecha de recepcion en SUNAT.',
    "2811": u'El XML no contiene el tag ResponseTime',
    "2812": u'ResponseTime - El dato ingresado  no cumple con el patrón hh:'
    u'mm:ss.sssss',
    "2813": u'El XML no contiene el tag o no existe información del Número '
    u'de documento de identificación del que envía el CPE (emisor o PSE)',
    "2814": u'El valor ingresado como Número de documento de identificación'
    u' del que envía el CPE (emisor o PSE) es incorrecto',
    "2816": u'El XML no contiene el atributo schemeID o no existe informaci'
    u'ón del Tipo de documento de identidad del que envía el CPE (emisor'
    u' o PSE)',
    "2817": u'El valor ingresado como Tipo de documento de identidad del qu'
    u'e envía el CPE (emisor o PSE) es incorrecto',
    "2818": u'El XML no contiene el atributo schemeAgencyName o no existe i'
    u'nformación del Tipo de documento de identidad del que envía el CPE'
    u' (emisor o PSE)',
    "2819": u'El valor ingresado en el atributo schemeAgencyName del Tipo d'
    u'e documento de identidad del que envía el CPE (emisor o PSE) es in'
    u'correcto',
    "2820": u'El XML no contiene el atributo schemeURI o no existe informac'
    u'ión del Tipo de documento de identidad del que envía el CPE (emiso'
    u'r o PSE)',
    "2821": u'El valor ingresado en el atributo schemeURI del Tipo de docum'
    u'ento de identidad del que envía el CPE (emisor o PSE) es incorrecto',
    "2822": u'El XML no contiene el tag o no existe información del Número '
    u'de documento de identificación del OSE',
    "2823": u'El valor ingresado como Número de documento de identificación'
    u' del OSE es incorrecto',
    "2824": u'El certificado digital con el que se firma el CDR OSE no corr'
    u'esponde con el RUC del OSE informado',
    "2825": u'El Número de documento de identificación del OSE informado no'
    u' esta registrado en el padron.',
    "2826": u'El XML no contiene el atributo schemeID o no existe informaci'
    u'ón del Tipo de documento de identidad del OSE',
    "2827": u'El valor ingresado como Tipo de documento de identidad del OS'
    u'E es incorrecto',
    "2828": u'El XML no contiene el atributo schemeAgencyName o no existe i'
    u'nformación del Tipo de documento de identidad del OSE',
    "2829": u'El valor ingresado en el atributo schemeAgencyName del Tipo d'
    u'e documento de identidad del OSE es incorrecto',
    "2830": u'El XML no contiene el atributo schemeURI o no existe informac'
    u'ión del Tipo de documento de identidad del OSE',
    "2831": u'El valor ingresado en el atributo schemeURI del Tipo de docum'
    u'ento de identidad del OSE es incorrecto',
    "2832": u'El XML no contiene el tag o no existe información del Código '
    u'de Respuesta',
    "2833": u'El valor ingresado como Código de Respuesta es incorrecto',
    "2834": u'El XML no contiene el atributo listAgencyName o no existe inf'
    u'ormación del Código de Respuesta',
    "2835": u'El valor ingresado en el atributo listAgencyName del Código d'
    u'e Respuesta es incorrecto',
    "2836": u'El XML no contiene el tag o no existe información de la Descr'
    u'ipción de la Respuesta',
    "2837": u'El valor ingresado como Descripción de la Respuesta es incorr'
    u'ecto',
    "2838": u'El valor ingresado como Código de observación es incorrecto',
    "2839": u'El XML no contiene el atributo listURI o no existe informació'
    u'n del Código de observación',
    "2840": u'El valor ingresado en el atributo listURI del Código de obser'
    u'vación es incorrecto',
    "2841": u'El XML no contiene el tag o no existe información de la Descr'
    u'ipción de la observación',
    "2842": u'El valor ingresado como Descripción de la observación es inco'
    u'rrecto',
    "2843": u'Se ha encontrado mas de una Descripción de la observación, ta'
    u'g cac:Response/cac:Status/cbc:StatusReason',
    "2844": u'No se encontro el tag cbc:StatusReasonCode cuando ingresó la '
    u'Descripción de la observación',
    "2845": u'El XML contiene mas de un elemento cac:DocumentReference',
    "2846": u'El XML no contiene informacion en el tag cac:DocumentReferenc'
    u'e/cbc:ID',
    "2848": u'El valor ingresado como Serie y número del comprobante no cor'
    u'responde con el del comprobante',
    "2849": u'El XML no contiene el tag o no existe información de la Fecha'
    u' de emisión del comprobante',
    "2851": u'El valor ingresado como Fecha de emisión del comprobante no c'
    u'orresponde con el del comprobante',
    "2852": u'El XML no contiene el tag o no existe información de la Hora '
    u'de emisión del comprobante',
    "2853": u'El valor ingresado como Hora de emisión del comprobante no cu'
    u'mple con el patrón hh:mm:ss.sssss',
    "2854": u'El valor ingresado como Hora de emisión del comprobante no co'
    u'rresponde con el del comprobante',
    "2855": u'El XML no contiene el tag o no existe información del Tipo de'
    u' comprobante',
    "2856": u'El valor ingresado como Tipo de comprobante es incorrecto',
    "2857": u'El valor ingresado como Tipo de comprobante no corresponde co'
    u'n el del comprobante',
    "2858": u'El XML no contiene el tag o no existe información del Hash de'
    u'l comprobante',
    "2859": u'El valor ingresado como Hash del comprobante es incorrecto',
    "2860": u'El valor ingresado como Hash del comprobante no corresponde c'
    u'on el del comprobante',
    "2861": u'El XML no contiene el tag o no existe información del Número '
    u'de documento de identificación del emisor',
    "2862": u'El valor ingresado como Número de documento de identificación'
    u' del emisor es incorrecto',
    "2863": u'El valor ingresado como Número de documento de identificación'
    u' del emisor no corresponde con el del comprobante',
    "2864": u'El XML no contiene el atributo o no existe información del Ti'
    u'po de documento de identidad del emisor',
    "2865": u'El valor ingresado como Tipo de documento de identidad del em'
    u'isor es incorrecto',
    "2866": u'El valor ingresado como Tipo de documento de identidad del em'
    u'isor no corresponde con el del comprobante',
    "2867": u'El XML no contiene el tag o no existe información del Número '
    u'de documento de identificación del receptor',
    "2868": u'El valor ingresado como Número de documento de identificación'
    u' del receptor es incorrecto',
    "2869": u'El valor ingresado como Número de documento de identificación'
    u' del receptor no corresponde con el del comprobante',
    "2870": u'El XML no contiene el atributo o no existe información del Ti'
    u'po de documento de identidad del receptor',
    "2871": u'El valor ingresado como Tipo de documento de identidad del re'
    u'ceptor es incorrecto',
    "2872": u'El valor ingresado como Tipo de documento de identidad del re'
    u'ceptor no corresponde con el del comprobante',
    "2873": u'El PSE informado no se encuentra vinculado con el  emisor del'
    u' comprobante en la fecha de comprobación',
    "2874": u'El Número de documento de identificación del OSE informado no'
    u' se encuentra vinculado al emisor del comprobante en la fecha de c'
    u'omprobación',
    "2875": u'ID - El dato ingresado no cumple con el formato R#-fecha-corr'
    u'elativo',
    "2876": u'La fecha de recepción del comprobante por OSE debe ser mayor '
    u'a la fecha de emisión del comprobante enviado',
    "2987": u'El comprobante ya fue informado y se encuentra anulado o '
    u'rechazado.',
    "4000": u'El documento ya fue presentado anteriormente.',
    "4001": u'El numero de RUC del receptor no existe.',
    "4002": u'Para el TaxTypeCode, esta usando un valor que no existe en el'
    u' catalogo.',
    "4003": u'El comprobante fue registrado previamente como rechazado.',
    "4004": u'El DocumentTypeCode de las guias debe existir y tener 2 posic'
    u'iones',
    "4005": u'El DocumentTypeCode de las guias debe ser 09 o 31',
    "4006": u'El ID de las guias debe tener informacion de la SERIE-NUMERO '
    u'de guia.',
    "4007": u'El XML no contiene el ID de las guias.',
    "4008": u'El DocumentTypeCode de Otros documentos relacionados no cumpl'
    u'e con el estandar.',
    "4009": u'El DocumentTypeCode de Otros documentos relacionados tiene va'
    u'lores incorrectos.',
    "4010": u'El ID de los documentos relacionados no cumplen con el estand'
    u'ar.',
    "4011": u'El XML no contiene el tag ID de documentos relacionados.',
    "4012": u'El ubigeo indicado en el comprobante no es el mismo que esta '
    u'registrado para el contribuyente.',
    "4013": u'El RUC  del receptor no esta activo',
    "4014": u'El RUC del receptor no esta habido',
    "4015": u'Si el tipo de documento del receptor no es RUC, debe tener op'
    u'eraciones de exportacion',
    "4016": u'El total valor venta neta de oper. gravadas IGV debe ser mayo'
    u'r a 0.00 o debe existir oper. gravadas onerosas',
    "4017": u'El total valor venta neta de oper. inafectas IGV debe ser may'
    u'or a 0.00 o debe existir oper. inafectas onerosas o de export.',
    "4018": u'El total valor venta neta de oper. exoneradas IGV debe ser ma'
    u'yor a 0.00 o debe existir oper. exoneradas',
    "4019": u'El calculo del IGV no es correcto',
    "4020": u'El ISC no esta informado correctamente',
    "4021": u'Si se utiliza la leyenda con codigo 2000, el importe de perce'
    u'pcion debe ser mayor a 0.00',
    "4022": u'Si se utiliza la leyenda con código 2001, el total de operaci'
    u'ones exoneradas debe ser mayor a 0.00',
    "4023": u'Si se utiliza la leyenda con código 2002, el total de operaci'
    u'ones exoneradas debe ser mayor a 0.00',
    "4024": u'Si se utiliza la leyenda con código 2003, el total de operaci'
    u'ones exoneradas debe ser mayor a 0.00',
    "4025": u'Si usa la leyenda de Transferencia o Servivicio gratuito, tod'
    u'os los items deben ser  no onerosos',
    "4026": u'No se puede indicar Guia de remision de remitente y Guia de r'
    u'emision de transportista en el mismo documento',
    "4027": u'El importe total no coincide con la sumatoria de los valores '
    u'de venta mas los tributos mas los cargos',
    "4028": u'El monto total de la nota de credito debe ser menor o igual a'
    u'l monto de la factura',
    "4029": u'El ubigeo indicado en el comprobante no es el mismo que esta '
    u'registrado para el contribuyente',
    "4030": u'El ubigeo indicado en el comprobante no es el mismo que esta '
    u'registrado para el contribuyente',
    "4031": u'Debe indicar el nombre comercial',
    "4032": u'Si el código del motivo de emisión de la Nota de Credito es 0'
    u'3, debe existir la descripción del item',
    "4033": u'La fecha de generación de la numeración debe ser menor o igua'
    u'l a la fecha de generación de la comunicación',
    "4034": u'El comprobante fue registrado previamente como baja',
    "4035": u'El comprobante fue registrado previamente como rechazado',
    "4036": u'La fecha de emisión de los rangos debe ser menor o igual a la'
    u' fecha de generación del resumen',
    "4037": u'El calculo del Total de IGV del Item no es correcto',
    "4038": u'El resumen contiene menos series por tipo de documento que el'
    u' envío anterior para la misma fecha de emisión',
    "4039": u'No ha consignado información del ubigeo del domicilio fiscal',
    "4040": u'Si el importe de percepcion es mayor a 0.00, debe utilizar un'
    u'a leyenda con codigo 2000',
    "4041": u'El codigo de pais debe ser PE',
    "4042": u'Para sac:SUNATTransaction/cbc:ID, se está usando un valor que'
    u' no existe en el catálogo. Nro. 17.',
    "4043": u'Para el TransportModeCode, se está usando un valor que no exi'
    u'ste en el catálogo Nro. 18.',
    "4044": u'PrepaidAmount: Monto total anticipado no coincide con la suma'
    u'toria de los montos por documento de anticipo.',
    "4045": u'No debe consignar los datos del transportista para la modalid'
    u'ad de transporte 02 – Transporte Privado.',
    "4046": u'No debe consignar información adicional en la dirección para '
    u'los locales anexos.',
    "4047": u'sac:SUNATTransaction/cbc:ID debe ser igual a 10 o igual a 11 '
    u'cuando ingrese información para sustentar el traslado.',
    "4048": u'cac:AdditionalDocumentReference/cbc:DocumentTypeCode - Contie'
    u'ne un valor no valido para documentos relacionado.',
    "4049": u'El numero de DNI del receptor no existe.',
    "4050": u'El numero de RUC del proveedor no existe.',
    "4051": u'El RUC del proveedor no esta activo.',
    "4052": u'El RUC del proveedor no esta habido.',
    "4053": u'Proveedor no debe ser igual al remitente o destinatario.',
    "4054": u'La guía no debe contener datos del proveedor.',
    "4055": u'El XML no contiene el atributo o no existe información en des'
    u'cripcion del motivo de traslado.',
    "4056": u'El XML no contiene el tag o no existe información en el tag S'
    u'plitConsignmentIndicator.',
    "4057": u'GrossWeightMeasure – El dato ingresado no cumple con el forma'
    u'to establecido.',
    "4058": u'cbc:TotalPackageQuantity - El dato ingresado no cumple con el'
    u' formato establecido.',
    "4059": u'Numero de bultos o pallets - información válida para importac'
    u'ión.',
    "4060": u'La guía no debe contener datos del transportista.',
    "4061": u'El numero de RUC del transportista no existe.',
    "4062": u'El RUC del transportista no esta activo.',
    "4063": u'El RUC del transportista no esta habido.',
    "4064": u'/DespatchAdvice/cac:Shipment/cac:ShipmentStage/cac:TransportM'
    u'eans/cbc:RegistrationNationalityID - El dato ingresado no cumple c'
    u'on el formato establecido.',
    "4065": u'cac:TransportMeans/cbc:TransportMeansTypeCode - El valor ingr'
    u'esado como tipo de unidad de transporte es incorrecta.',
    "4066": u'El numero de DNI del conductor no existe.',
    "4067": u'El XML no contiene el tag o no existe informacion del ubigeo '
    u'del punto de llegada.',
    "4068": u'Direccion de punto de lllegada - El dato ingresado no cumple '
    u'con el formato establecido.',
    "4069": u'CityName - El dato ingresado no cumple con el formato estable'
    u'cido.',
    "4070": u'District - El dato ingresado no cumple con el formato estable'
    u'cido.',
    "4071": u'Numero de Contenedor - El dato ingresado no cumple con el for'
    u'mato establecido.',
    "4072": u'Numero de contenedor - información válida para importación.',
    "4073": u'TransEquipmentTypeCode - El valor ingresado como tipo de cont'
    u'enedor es incorrecta.',
    "4074": u'Numero Precinto - El dato ingresado no cumple con el formato '
    u'establecido.',
    "4075": u'El XML no contiene el tag o no existe informacion del ubigeo '
    u'del punto de partida.',
    "4076": u'Direccion de punto de partida - El dato ingresado no cumple c'
    u'on el formato establecido.',
    "4077": u'CityName - El dato ingresado no cumple con el formato estable'
    u'cido.',
    "4078": u'District - El dato ingresado no cumple con el formato estable'
    u'cido.',
    "4079": u'Código de Puerto o Aeropuerto - El dato ingresado no cumple c'
    u'on el formato establecido.',
    "4080": u'Tipo de Puerto o Aeropuerto - El dato ingresado no cumple con'
    u' el formato establecido.',
    "4081": u'El XML No contiene El tag o No existe información del Numero '
    u'de orden del item.',
    "4082": u'Número de Orden del Ítem - El orden del ítem no cumple con el'
    u' formato establecido.',
    "4083": u'Cantidad - El dato ingresado no cumple con el formato estable'
    u'cido.',
    "4084": u'Descripción del Ítem - El dato ingresado no cumple con el for'
    u'mato establecido.',
    "4085": u'Código del Ítem - El dato ingresado no cumple con el formato '
    u'establecido.',
    "4086": u'El emisor y el cliente son Agentes de percepción de combustib'
    u'le en la fecha de emisión.',
    "4087": u'El Comprobante de Pago Electrónico no está Registrado en los '
    u'Sistemas de la SUNAT.',
    "4088": u'El Comprobante de Pago no está autorizado en los Sistemas de '
    u'la SUNAT.',
    "4089": u'La operación con este cliente está excluida del sistema de pe'
    u'rcepción. Es agente de retención.',
    "4090": u'La operación con este cliente está excluida del sistema de pe'
    u'rcepción. Es entidad exceptuada de la percepción.',
    "4091": u'La operación con este proveedor está excluida del sistema de '
    u'retención. Es agente de percepción, agente de retención o buen con'
    u'tribuyente.',
    "4092": u'El nombre comercial del emisor no cumple con el formato estab'
    u'lecido',
    "4093": u'El ubigeo del emisor no cumple con el formato establecido o n'
    u'o es válido',
    "4094": u'La dirección completa y detallada del domicilio fiscal del em'
    u'isor no cumple con el formato establecido',
    "4095": u'La urbanización del domicilio fiscal del emisor no cumple con'
    u' el formato establecido',
    "4096": u'La provincia del domicilio fiscal del emisor no cumple con el'
    u' formato establecido',
    "4097": u'El departamento del domicilio fiscal del emisor no cumple con'
    u' el formato establecido',
    "4098": u'El distrito del domicilio fiscal del emisor no cumple con el '
    u'formato establecido',
    "4099": u'El nombre comercial del cliente no cumple con el formato esta'
    u'blecido',
    "4100": u'El ubigeo del cliente no cumple con el formato establecido o '
    u'no es válido',
    "4101": u'La dirección completa y detallada del domicilio fiscal del cl'
    u'iente no cumple con el formato establecido',
    "4102": u'La urbanización del domicilio fiscal del cliente no cumple co'
    u'n el formato establecido',
    "4103": u'La provincia del domicilio fiscal del cliente no cumple con e'
    u'l formato establecido',
    "4104": u'El departamento del domicilio fiscal del cliente no cumple co'
    u'n el formato establecido',
    "4105": u'El distrito del domicilio fiscal del cliente no cumple con el'
    u' formato establecido',
    "4106": u'El nombre comercial del proveedor no cumple con el formato es'
    u'tablecido',
    "4107": u'El ubigeo del proveedor no cumple con el formato establecido '
    u'o no es válido',
    "4108": u'La dirección completa y detallada del domicilio fiscal del pr'
    u'oveedor no cumple con el formato establecido',
    "4109": u'La urbanización del domicilio fiscal del proveedor no cumple '
    u'con el formato establecido',
    "4110": u'La provincia del domicilio fiscal del proveedor no cumple con'
    u' el formato establecido',
    "4111": u'El departamento del domicilio fiscal del proveedor no cumple '
    u'con el formato establecido',
    "4112": u'El distrito del domicilio fiscal del proveedor no cumple con '
    u'el formato establecido',
    "4120": u'El XML no contiene o no existe informacion en el tag SUNATEmb'
    u'ededDespatchAdvice de Información que sustenta el traslado.',
    "4121": u'Para el tipo de operación no se consigna el tag SUNATEmbededD'
    u'espatchAdvice de Información de sustento de traslado.',
    "4122": u'Factura con información que sustenta el traslado, debe regist'
    u'rar leyenda 2008.',
    "4123": u'sac:SUNATEmbededDespatchAdvice - Para Factura Electrónica Rem'
    u'itente no se consigna datos en documento de referencia(cac:OrderRe'
    u'ference).',
    "4124": u'cac:Shipment - Para Factura Electrónica Remitente debe indica'
    u'r sujeto que realiza el traslado de bienes (1: Vendendor o 2: Comp'
    u'rador).',
    "4125": u'cac:Shipment - Para Factura Electrónica Remitente debe indica'
    u'r modalidad de transporte para el sustento de traslado de bienes ('
    u'cbc:TransportModeCode).',
    "4126": u'cac:Shipment - Debe indicar fecha de inicio de traslado para '
    u'el  sustento de traslado de bienes (cac:TransitPeriod/cbc:StartDat'
    u'e).',
    "4127": u'cac:Shipment - Para Factura Electrónica Remitente debe indica'
    u'r el punto de partida para el sustento de traslado de bienes (cac:'
    u'DeliveryAddrees).',
    "4128": u'cac:Shipment - Para Factura Electrónica Remitente debe indica'
    u'r el punto de llegada para el sustento de traslado de bienes (cac:'
    u'OriginAddress).',
    "4129": u'sac:SUNATEmbededDespatchAdvice - Para Factura Electrónica Rem'
    u'itente no se consigna indicador de subcontratación (cbc:MarkAttent'
    u'ionIndicator).',
    "4130": u'sac:SUNATEmbededDespatchAdvice - Para Factura Electrónica Rem'
    u'itente debe consignar datos en documento de referencia (cac:OrderR'
    u'eference).',
    "4131": u'sac:SUNATEmbededDespatchAdvice - Para Factura Electrónica Tra'
    u'nsportista no se consigna destinatario para el sustento de traslad'
    u'o de bienes (cac:DeliveryCustomerParty).',
    "4132": u'cac:Shipment - Para Factura Electrónica Transportista no se c'
    u'onsigna sujeto que realiza el traslado (cbc:HandlingCode).',
    "4133": u'cac:Shipment - Para Factura Electrónica Transportista no se c'
    u'onsigna peso total de la factura para el sustento de traslado de b'
    u'ienes (cbc:GrossWeightMeasure).',
    "4134": u'cac:Shipment - Para Factura Electrónica Transportista no se c'
    u'onsigna modalidad de transporte para el sustento de traslado de bi'
    u'enes (cbc:TransportModeCode).',
    "4135": u'cac:Shipment - Para Factura Electrónica Transportista no se c'
    u'onsigna punto de llegada para el sustento de traslado de bienes (c'
    u'ac:DeliveryAddress).',
    "4136": u'cac:Shipment - Para Factura Electrónica transportista no se c'
    u'onsigna punto de partida para el sustento de traslado de bienes (c'
    u'ac:OriginAddress).',
    "4137": u'cac:OrderReference - Debe consignar número de  documento de r'
    u'eferencia que sustenta el traslado (./cbc:ID).',
    "4138": u'cac:OrderReference - Debe consignar tipo de documento de refe'
    u'rencia que sustenta el traslado (./cbc:OrderTypeCode).',
    "4139": u'cac:OrderReference - Tipo de documento de referencia que sust'
    u'enta el traslado no válido (01 – Factura o 09 – Guía de Remisión).',
    "4140": u'cac:OrderReference - Serie-Numero ingresado en documento de r'
    u'eferencia que sustenta el traslado no cumple con el formato establ'
    u'ecido.',
    "4141": u'cac:OrderReference - Debe consignar RUC emisor del documento '
    u'de referencia que sustenta el traslado (./cac:DocumentReference/ca'
    u'c:IssuerParty/cac:PartyIdentification/cbc:ID).',
    "4142": u'cac:OrderReference -  RUC emisor del documento de referencia '
    u'que sustenta el traslado no cumple con el formato establecido.',
    "4143": u'cac:OrderReference – RUC Emisor de documento de referencia qu'
    u'e sustenta el traslado no existe o se encuentra dado de baja.',
    "4144": u'cac:OrderReference – Documento de Referencia ingresado no cor'
    u'responde a un comprobante electrónico declarado y activo en SUNAT.',
    "4145": u'cac:OrderReference – Documento de Referencia ingresado no cor'
    u'responde comprobante autorizado por SUNAT.',
    "4146": u'cac:OrderReference - Nombre o razon social del emisodr de ref'
    u'erencia que sustenta el traslado de bienes no cumple con un format'
    u'o válido.',
    "4147": u'cac:DeliveryCustomerParty - Debe consignar numero de document'
    u'o de identidad del destinatario (cbc:CustomerAssignedAccountID).',
    "4148": u'cac:DeliveryCustomerParty - Debe consignar tipo de documento '
    u'de identidad del destinatario (cbc:CustomerAssignedAccountID/@sche'
    u'meID).',
    "4149": u'cac:DeliveryCustomerParty - Tipo de documento de identidad de'
    u'l destinatario no válido (Catálogo N° 06).',
    "4150": u'cac:DeliveryCustomerParty - Numero de documento de identidad '
    u'del destinatario no cumple con un formato válido.',
    "4151": u'cac:DeliveryCustomerParty - Debe consignar apellidos y nombre'
    u's, denominación o razón social del destinatario (cac:Party/cac:Par'
    u'tyLegalEntity/cbc:RegistrationName).',
    "4152": u'cac:DeliveryCustomerParty - Nombre o razon social del destina'
    u'tario no cumple con un formato válido.',
    "4153": u'cbc:HandlingCode - Sujeto que realiza el traslado no es valido.',
    "4154": u'cbc:GrossWeightMeasure@unitCode: El valor ingresado en la uni'
    u'dad de medida para el peso bruto total no es correcta (KGM).',
    "4155": u'GrossWeightMeasure – El valor ingresado no cumple con el esta'
    u'ndar.',
    "4156": u'Debe ingresar la totalidad de la información requerida al tra'
    u'nsportista.',
    "4157": u'No existe información en el tag datos de conductores.',
    "4158": u'No existe información en el tag datos de vehículos.',
    "4159": u'No es necesario consignar los datos del transportista para un'
    u'a operación de Transporte Privado.',
    "4160": u'cac:CarrierParty: Debe consignar número de  documento de iden'
    u'tidad del transportista.',
    "4161": u'cac:CarrierParty: Debe consignar tipo de documento de identid'
    u'ad del transportista.',
    "4162": u'cac:CarrierParty: Tipo de documento de identidad del transpor'
    u'tista no válido (06 - RUC).',
    "4163": u'cac:CarrierParty: Numero de documento de identidad del transp'
    u'ortista no cumple con un formato válido.',
    "4164": u'cac:CarrierParty: Debe consignar apellidos y nombres, denomin'
    u'ación o razón social del transportista.',
    "4165": u'cac:CarrierParty: nombre o razon social del transportista no '
    u'cumple con un formato válido.',
    "4166": u'cac: TransportHandlingUnit: Numero de placa (cbc:ID) no coinc'
    u'ide con el numero de placa del vehiculo prinicipal.',
    "4167": u'cac:RoadTransport/cbc:LicensePlateID: Numero de placa del veh'
    u'ículo no cumple con el formato válido.',
    "4168": u'cac: TransportHandlingUnit: Numero de placa del vehículo prin'
    u'cipal no existe o no cumple con el formato válido (cbc:ID).',
    "4169": u'cac:TransportEquipment: debe consignar al menos un vehiculo s'
    u'ecundario.',
    "4170": u'cac:TransportEquipment: Numero de placa del vehículo principa'
    u'l no existe o no cumple con el formato válido (cbc:ID).',
    "4171": u'cac:DriverPerson: Debe consignar número de  documento de iden'
    u'tidad del conductor (cbc:ID).',
    "4172": u'cac:DriverPerson: Debe consignar tipo de documento de identid'
    u'ad del conductor (cbc:ID/@schemeID).',
    "4173": u'cac:DriverPerson: Tipo de documento de identidad del conducto'
    u'r no válido (Catalogo Nro 06).',
    "4174": u'cac:DriverPerson: Numero de documento de identidad del conduc'
    u'tor no cumple con el formato válido.',
    "4175": u'cac:DeliveryAddress: Debe consignar código de ubigeo de punto'
    u' de llegada (cbc:ID).',
    "4176": u'cac:DeliveryAddress: Código de ubigeo de punto de llegada no '
    u'cumple con el formato válido.',
    "4177": u'cac:DeliveryAddress: Debe consignar código de ubigeo válido ('
    u'Catálogo N° 13).',
    "4178": u'cac:DeliveryAddress: Debe consignar Dirección del punto de ll'
    u'egada (cbc:StreetName).',
    "4179": u'cac:DeliveryAddress: Dirección completa y detallada del punto'
    u' de llegada no cumple con el formato válido.',
    "4180": u'cac:OriginAddress: Debe consignar código de ubigeo de punto d'
    u'e partida (cbc:ID).',
    "4181": u'cac:OriginAddress: Código de ubigeo de punto de llegada no cu'
    u'mple con el formato válido.',
    "4182": u'cac:OriginAddress: Debe consignar código de ubigeo válido (Ca'
    u'tálogo N° 13).',
    "4183": u'cac:OriginAddress: Debe consignar Dirección detallada del pun'
    u'to de partida (cbc:StreetName).',
    "4184": u'cac:OriginAddres: Dirección completa y detallada del punto de'
    u' partida no cumple con el estandar.',
    "4185": u'cac:OrderReference - Serie y numero no se encuentra registrad'
    u'o como baja por cambio de destinatario.',
    "4186": u'cbc:Note - El campo observaciones supera la cantidad maxima e'
    u'specificada (250 carácteres).',
    "4187": u'cac:OrderReference - El campo Tipo de documento (descripción)'
    u' supera la cantidad maxima especificada (50 carácteres).',
    "4188": u'El XML no contiene el atributo o no existe información del no'
    u'mbre o razon social del tercero relacionado.',
    "4189": u'El valor ingresado como tipo de documento del nombre o razon '
    u'social del tercero relacionado es incorrecto.',
    "4190": u'El valor ingresado como descripcion de motivo de traslado no '
    u'cumple con el estandar.',
    "4191": u'Para el motivo de traslado, no se consigna información en el '
    u'numero de DAM.',
    "4192": u'Para el motivo de traslado, no se consigna información del ma'
    u'nifiesto de carga.',
    "4193": u'El valor ingresado como indicador de transbordo programado no'
    u' cumple con el estandar.',
    "4194": u'El XML no contiene el atributo o no existe información en pes'
    u'o bruto total de la guia.',
    "4195": u'Numero de bultos o pallets es una información válida solo par'
    u'a importación.',
    "4196": u'La fecha de recepción en SUNAT es mayor a 1 hora(s) respecto '
    u'a la fecha de comprobación por OSE',
    "4197": u'IssueTime - El dato ingresado  no cumple con el patrón hh:mm:'
    u'ss.sssss',
    "4230": u'el Comprobante no debió ser observado.',
}


def l10n_pe_edi_get_error_by_code(code_str):
    return CODES.get(code_str) or _('Error code not recognized')
