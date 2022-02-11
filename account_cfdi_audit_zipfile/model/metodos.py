# -*- encoding: utf-8 -*-

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import api, exceptions, fields, models, _
#import odoo.addons.decimal_precision as dp
import time
from datetime import datetime, timedelta
import base64
import os
import zipfile
import subprocess
import tempfile
from xml.dom.minidom import parse, parseString
import xmltodict
import requests
import logging
_logger = logging.getLogger(__name__)


from io import BytesIO
    
class AccountCFDI(models.Model):
    _inherit = "account.cfdi"    
    
    def link_cfdi(self):
        attachment = self.env['ir.attachment'].create({'name':self.x_f_name,'datas':self.x_file}).id
        context = {
            'default_subtotal': (self.total)*-1, 
            'default_attachment_ids': [(4,attachment)],
            'default_rfc': self.rfc_emisor,
        }
        _logger.info('Context = '+str(context))
        return {
                'name': _('Link invoice'),
                'view_mode': 'form',
                'res_model': 'account.cfdi.wizard.link.cfdi',
                'view_id': self.env.ref('account_cfdi_audit_zipfile.account_cfdi_wizard_link_cfdi_form_view').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
    #@api.multi
    def audit_cfdis(self):
        invoice_obj = self.env['account.move']
        payment_obj = self.env['account.payment']
        #complms_obj = self.env['eaccount.complements']
        cfdi_wiz_obj = self.env['account.cfdi.wizard.zipfile']
        parameter =  1
        _logger.info(u'Iniciando proceso de revisión de CFDIs')
        for cfdi in self:
            _logger.info(u'Revisando UUID %s' % cfdi.folio_fiscal)
            cfdi.sat_estado = cfdi_wiz_obj.check_cfdi_satus(cfdi.folio_fiscal,cfdi.rfc_emisor, cfdi.rfc_receptor,cfdi.total).replace(' ','_')
            _logger.info('Vigencia UUID: %s' % (cfdi.sat_estado))
            cfdi.date_sat_estado = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)            
            cfdi.date_audit = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            invoices = invoice_obj.search([('l10n_mx_edi_cfdi_uuid','in',(cfdi.folio_fiscal.upper(), cfdi.folio_fiscal.lower()))])
            payments = payment_obj.search([('l10n_mx_edi_cfdi_uuid','in',(cfdi.folio_fiscal.upper(), cfdi.folio_fiscal.lower()))])
            #complements = complms_obj.search([('uuid','in',(cfdi.folio_fiscal.upper(), cfdi.folio_fiscal.lower()))])
            _logger.info("\n######################################################################")
            _logger.info("\n############### invoices >>>>>>>>>>>>>>>>>>>>> %s " % invoices)
            _logger.info("\n############### payments >>>>>>>>>>>>>>>>>>>>> %s " % payments)
            #_logger.info("\n############### complements >>>>>>>>>>>>>>>>>>>>> %s " % complements)
            #_logger.info("\n######################################################################")
            if not (invoices or payments): #or complements)
                _logger.info('Entra 1')
                cfdi.state='error01'  # No existe el registro en Odoo
                cfdi.message_post(body=u"No existe el registro en Odoo (Facturas / Pagos / Complementos de Contabilidad Electrónica)")
                continue
            if invoices:
                _logger.info('Entra 2')
                invoices.write({'cfdi_id':cfdi.id})
                if len(invoices) > 1:
                    _logger.info('Entra 3')
                    cfdi.state='error02' # Existe mas de una vez en las Facturas
                    cfdi.message_post(body=u"Existe mas de un registro de Factura en Odoo con el mismo CFDI")
                    continue
                low = invoices.amount_total 
            
            
                upp = invoices.amount_total
            
                if not low == cfdi.total:
                    _logger.info('Entra 4')
                    cfdi.state='error03' # El total de la factura no es igual al total del CFDI
                    cfdi.message_post(body=u"El monto de la Factura %s - Ref: %s (%.2f) es diferente al monto del CFDI (%.2f)" % (invoices.name, invoices.ref, invoices.amount_total, cfdi.total))
                    continue
                if cfdi.currency_id != invoices.currency_id:
                    _logger.info('Entra 5')
                    cfdi.state='error04' # La Moneda de la Factura no corresponde a la moneda del CFDI
                    cfdi.message_post(body=u"La moneda de la Factura %s - Ref: %s (%s) es diferente a la moneda del CFDI (%s)" % (invoices.name, invoices.ref, invoices.currency_id.name, cfdi.currency_id.name))
                    continue
                if cfdi.sat_estado == 'vigente' and invoices.state == 'cancel':
                    _logger.info('Entra 6')
                    cfdi.state='error05' # La factura está cancelada pero el CFDI esta Vigente
                    cfdi.message_post(body=u"La Factura %s - Ref: %s está Cancelada pero el CFDI está Vigente" % (invoices.name, invoices.ref))
                    continue
                if cfdi.sat_estado != 'vigente' and invoices.state != 'cancel':
                    _logger.info('Entra 7')
                    cfdi.state='error06' # El CFDI está Cancelado pero la factura NO lo está
                    cfdi.message_post(body=u"El CFDI está Cancelado pero la Factura %s - Ref: %s NO lo está" % (invoices.name, invoices.ref))
                    continue
                
                cfdi.state='ok'
            if payments:
                _logger.info('Entra 8')
                payments.write({'cfdi_id':cfdi.id})
                if len(payments) > 1:
                    _logger.info('Entra 9')
                    cfdi.state='error10' # Existe mas de una vez en los Recibos Electrónicos de Pago
                    cfdi.message_post(body=u"Existe mas de un registro de Pagos en Odoo con el mismo CFDI")
                    continue
                low = payments.amount - parameter
                upp = payments.amount + parameter
                if not low < cfdi.monto_pago < upp:
                    _logger.info('Entra 10')
                    cfdi.state='error11' # El total del Monto del Pago no es igual al Monto del pago del CFDI
                    cfdi.message_post(body=u"El monto del Pago %s - Ref: %s (%.2f) es diferente al monto del Pago del Complemento del CFDI (%.2f)" % (payments.name, payments.communication, payments.amount, cfdi.monto_pago))
                    continue
                if cfdi.pago_currency_id != payments.currency_id:
                    _logger.info('Entra 11')
                    cfdi.state='error12' # La Moneda del Pago no corresponde a la moneda del CFDI
                    cfdi.message_post(body=u"La moneda del Pago %s - Ref: %s (%s) es diferente a la moneda del CFDI (%s)" % (payments.name, payments.communication, payments.pago_currency_id.name, cfdi.currency_id.name))
                    continue
                if cfdi.sat_estado == 'vigente' and payments.state == 'cancel':
                    _logger.info('Entra 12')
                    cfdi.state='error13' # La factura está cancelada pero el CFDI esta Vigente
                    cfdi.message_post(body=u"El Pago %s - Ref: %s está Cancelada pero el CFDI está Vigente" % (payments.name, payments.communication))
                    continue
                if cfdi.sat_estado != 'vigente' and payments.state != 'cancel':
                    _logger.info('Entra 13')
                    cfdi.state='error14' # El CFDI está Cancelado pero el Pago NO lo está
                    cfdi.message_post(body=u"El CFDI está Cancelado pero el Pago %s - Ref: %s NO lo está" % (payments.name, payments.communication))
                    continue                    
                cfdi.state='ok'
            """
            if complements:
                complements.write({'cfdi_id' : cfdi.id})
                move_ids = []
                for complement in complements:
                    if move_ids:
                        if complement.move_id.id in move_ids:
                            cfdi.state='error20' # EL UUID existe mas de una vez en una misma póliza
                            cfdi.message_post(body=u"Existe mas de un registro de Pagos en Odoo con el mismo CFDI en la misma póliza")
                            continue
                    move_ids.append(complement.move_id.id)
                    if complement.compl_currency_id != cfdi.currency_id:
                        cfdi.state='error21' # La Moneda del Complemento de Contabilidad Electrónica es diferente a la moneda del CFDI
                        cfdi.message_post(body=u"La moneda del Complemento de Contabilidad Electrónica de la Póliza %s - Partida: %s (%s) es diferente a la moneda del CFDI (%s)" % (complement.move_id.name, complement.move_line_id.name, complement.compl_currency_id.name, cfdi.currency_id.name))
                        continue
                        
                cfdi.state='ok'
            """    
        return True


class AccountCFDItWizardZipFile(models.TransientModel):
    _inherit = 'account.cfdi.wizard.zipfile'

    #@api.multi
    def get_cfdis_from_zipfile(self):
        account_cfdi_obj = self.env['account.cfdi']
        currency_obj = self.env['res.currency']
        (fileno, fname) = tempfile.mkstemp('sat_cfdi_zip_', '.zip')
        f = open(fname, 'wb')
        f.write(base64.decodestring(self.zip_file))
        f.close()
        os.close(fileno)
        try:
            archivo_zip = zipfile.ZipFile(fname, 'r')
        except:
            archivo_zip = False
        if not archivo_zip:
            raise UserError(_("Error ! El archivo no es un archivo ZIP o no contiene archivos XML de CFDIs..."))
        
        cfdi_ids = []
        for file_name in archivo_zip.namelist():
            _logger.info(_('Importando: %s') % (file_name))
            with archivo_zip.open(file_name) as src_f:
                chunk_str = src_f.read()
                #_logger.info(_( "ALV"  ) ) 
                #_logger.info(_( src_f  ) ) 
             
                #chunk_stream = BytesIO(chunk_str)
                #chunk_bytes = chunk_stream.read()
               
            try:
                x = file_name.split('.')[1]
            except:
                continue
            if file_name.split('.')[1] != 'xml':
                _logger.info(_('Archivo %s descartado porque no es un archivo XML') % (file_name))
                continue
            
            _logger.info(_("-- Procesando: %s") % file_name)

            chunk_stream = BytesIO(archivo_zip.read(file_name))
            chunk_bytes = chunk_stream.read()
            cfdi_str = archivo_zip.read(file_name).decode("utf-8").replace('\xef\xbb\xbf','')            
            cfdi_str = cfdi_str.lower()
            try: 
                arch_xml = parseString(cfdi_str)
            except:
                _logger.info(_('Error al procesar archivo %s donde al parecer no es archivo XML') % (file_name))
                continue
            #res = account_cfdi_obj.search([('folio_fiscal','=',file_name.split('.')[0].upper())])    
            timbre = arch_xml.getElementsByTagName('tfd:timbrefiscaldigital')[0] 
            folio_fiscal_from_xml = timbre.attributes['uuid'].value.upper()
            res = account_cfdi_obj.search([('folio_fiscal','=',folio_fiscal_from_xml)])   
            if not res:
                timbre = arch_xml.getElementsByTagName('tfd:timbrefiscaldigital')[0]    
                cfdi_data = arch_xml.getElementsByTagName('cfdi:comprobante')[0]
                data = {
                    #'clasificacion_cfdi':*
                    'tipo_cfdi'         : cfdi_data.attributes['tipodecomprobante'].value.upper() or False,
                    'folio_fiscal'      : timbre.attributes['uuid'].value.upper(),
                    'subtotal'          : cfdi_data.attributes['subtotal'].value,
                    'total'             : cfdi_data.attributes['total'].value,
                    'no_certificado'    : cfdi_data.attributes['nocertificado'].value.upper() or False,
                    }
                
                try:
                    data['pay_method'] = cfdi_data.attributes['metodopago'].value.upper() or False
                except:
                    pass
                # try:
                #     receptor = arch_xml.getElementsByTagName('cfdi:receptor')[0]
                #     data['uso_cfdi'] = receptor.attributes['usocfdi'].value.upper() or False
                # except:
                #     pass
    
                if data['tipo_cfdi'] == 'P':
                    data['monto_pago'] = 0.0
                    cadena = ['pago10:pago', 'pag:pago', 'pag:Pago']
                    root = 'pago10:pago'
                    for cad in cadena:
                        try:
                            w = arch_xml.getElementsByTagName(cad)
                            root = cad
                        except:
                            pass
                    try:
                        for pago in arch_xml.getElementsByTagName(root):                        
                            data['monto_pago'] += pago.attributes['Monto'].value and round(float(pago.attributes['Monto'].value),4) or 0.0
                            moneda = False
                            try:
                                moneda = pago.attributes['monedap'].value.upper()
                            except:
                                pass
                            if moneda and moneda not in ('MN','MXN','PESOS', 'PESOS MEXICANOS','NACIONAL'):
                                currency_id = currency_obj.search([('name','=',moneda)], limit=1)                
                                if currency_id:
                                    data['pago_currency_id'] = currency_id.id
                    except:
                        pass
                    
                htz = -6
                fecha_timbrado = timbre.attributes['fechatimbrado'].value or False
                fecha_timbrado = fecha_timbrado and time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(fecha_timbrado[:19], '%Y-%m-%dt%H:%M:%S')) or False
                data['fecha_certificacion'] = fecha_timbrado and datetime.strptime(fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False

                fecha_emision = cfdi_data.attributes['fecha'].value or False
                fecha_emision = fecha_emision and time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(fecha_emision[:19], '%Y-%m-%dt%H:%M:%S')) or False
                data['fecha_emision'] = fecha_emision and datetime.strptime(fecha_emision, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False

                try:
                    data['serie'] = cfdi_data.attributes['serie'].value.upper()
                except:
                    pass
                try:
                    data['folio'] = cfdi_data.attributes['folio'].value.upper()
                except:
                    pass

                moneda = False
                try:
                    moneda = cfdi_data.attributes['moneda'].value.upper()
                except:
                    pass

                if moneda and moneda not in ('MN','MXN','PESOS', 'PESOS MEXICANOS','NACIONAL'):
                    currency_id = currency_obj.search([('name','=',moneda)], limit=1)                
                    if currency_id:
                        data['currency_id'] = currency_id.id

                cfdi_emisor = arch_xml.getElementsByTagName('cfdi:emisor')[0]
                data['rfc_emisor'] = cfdi_emisor.attributes['rfc'].value.upper()
                try:
                    data['razon_social_emisor'] = cfdi_emisor.attributes['nombre'].value.upper()
                except:
                    pass
                cfdi_receptor = arch_xml.getElementsByTagName('cfdi:receptor')[0]
                data['rfc_receptor'] = cfdi_receptor.attributes['rfc'].value.upper()
                try:
                    data['razon_social_receptor'] = cfdi_receptor.attributes['nombre'].value.upper()
                except:
                    pass
                try:
                    data['uso_cfdi'] = cfdi_receptor.attributes['usocfdi'].value.upper() or False
                except:
                    pass
                data['x_file'] = base64.encodestring(chunk_bytes)
                data['x_f_name'] = file_name
              
              
                res = account_cfdi_obj.create(data)
            else:
                data = {}
                cfdi_data = arch_xml.getElementsByTagName('cfdi:comprobante')[0]                
                data['folio_fiscal'] = file_name.split('.')[0].upper()
                cfdi_emisor = arch_xml.getElementsByTagName('cfdi:emisor')[0]
                data['rfc_emisor'] = cfdi_emisor.attributes['rfc'].value.upper()
                cfdi_receptor = arch_xml.getElementsByTagName('cfdi:receptor')[0]
                data['rfc_receptor'] = cfdi_receptor.attributes['rfc'].value.upper()
                data['total'] = cfdi_data.attributes['total'].value and round(float(cfdi_data.attributes['total'].value),4) or 0.0
                
            #_logger.info('Revisando Vigencia: %s' % (data['folio_fiscal']))
            #res.write({'sat_estado': self.check_cfdi_satus(data['folio_fiscal'],data['rfc_emisor'], data['rfc_receptor'],data['total']).replace(' ','_'), 'date_sat_estado': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            for x in res:
                cfdi_ids.append(x.id)
            
        archivo_zip.close()
        if cfdi_ids:
            return {
                    'domain'    : "[('id','in', ["+','.join(map(str,cfdi_ids))+"])]",
                    'name'      : _('CFDIs Descargados del Portal del SAT'),
                    'view_type' : 'form',
                    'view_mode' : 'tree,form',
                    'res_model' : 'account.cfdi',
                    'view_id'   : False,
                    'type'      : 'ir.actions.act_window'
                    }
        else:
            raise UserError(_('Advertencia !!!\nNo se encontró ningún archivo XML en el archivo ZIP que subió...'))
            
        ########################################
        
    def check_cfdi_satus(self, folio_fiscal, rfc_emisor, rfc_receptor, total):        
        result, res = False, False
        estado_cfdi = ''
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/"><soapenv:Header/><soapenv:Body><tem:Consulta><!--Optional:--><tem:expresionImpresa><![CDATA[?re={0}&rr={1}&tt={2}&id={3}]]></tem:expresionImpresa></tem:Consulta></soapenv:Body></soapenv:Envelope>
                        """
        url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'
        headers = {'Content-type': 'text/xml;charset="utf-8"', 
                   'Accept' : 'text/xml', 
                   'SOAPAction': 'http://tempuri.org/IConsultaCFDIService/Consulta'}
        try:
            #-------------
            bodyx = body.format(rfc_emisor, rfc_receptor, total, folio_fiscal)
            result = requests.post(url=url, headers=headers, data=bodyx)
            res = xmltodict.parse(result.text)
            if result.status_code == 200:
                estado_cfdi = res['s:Envelope']['s:Body']['ConsultaResponse']['ConsultaResult']['a:Estado']
                return estado_cfdi.lower()
            else:
                _logger.info('\nNo se pudo establecer la conexión con el sitio del SAT para validar la factura, por favor revise su conexión de internet y/o espere a que el sitio del SAT se encuentre disponible...\n')
                return 'error'
            #-------------
        except:
            _logger.info('\nNo se pudo establecer la conexión con el sitio del SAT para validar la factura, por favor revise su conexión de internet y/o espere a que el sitio del SAT se encuentre disponible...\n')
            return 'error'


        
     
