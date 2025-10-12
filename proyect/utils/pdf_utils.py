from django.http import HttpResponse
from django.utils import timezone #Para ver la hora correctamente.

from ..models import WorkOrder, Proyect, ProyectDecorator, Item, CalendarItem, ItemAttribute, ItemAttributeNote, ItemMaterial, ItemImage

from xhtml2pdf import pisa #Para el PDF
from django.template.loader import get_template #Para el PDF
from django.http import Http404 #Para el PDF
from django.conf import settings #Para el PDF, manejar las rutas
from django.contrib.staticfiles import finders
import os
import io


def generate_pdf(request, workorderId):
    try:
        wo = WorkOrder.objects.get(id=workorderId)
    except Proyect.DoesNotExist:
        raise Http404("El proyecto no existe")
    
    htmlCabecera = ""
    
    if wo:

        #Cabecera cliente

        # htmlCabecera += "<table class='table_wo'>"
        
        # address = ''

        # if wo.proyect.customer:

        #     if wo.proyect.customer.address != "":
        #         address += wo.proyect.customer.address

        #     if wo.proyect.customer.apartment != "":
        #         address += "," + wo.proyect.customer.apartment

        #     if wo.proyect.customer.city != "":
        #         address += "," + wo.proyect.customer.city

        #     if wo.proyect.customer.state != "":
        #         address += "," + wo.proyect.customer.state

        #     if wo.proyect.customer.zipcode != "":
        #         address += "," + wo.proyect.customer.zipcode
        
        # name = wo.proyect.customer.name if str(wo.proyect.customer.name) != "" else "--"
        # phone = wo.proyect.customer.phone if str(wo.proyect.customer.phone) != "" else "--"
        # email = wo.proyect.customer.email if str(wo.proyect.customer.email) != "" else "--"

        # code = wo.proyect.code if str(wo.proyect.code) != "" else "--"
        
        
        # htmlCabecera += "<tr><th colspan=2></th><th></th><th>Code:</th><td>" + str(code) + "</td></tr>"
        # htmlCabecera += "<tr><th style='width: 88px'>Address:</th><td style='width: 340px'>" + address + "</td><th></th><th style='width: 80px'>Phone:</th><td style='width: 250px'>" + str(phone) + "</td></tr>"
        # htmlCabecera += "<tr><th>Customer:</th><td>" + str(name) + "</td><th></th><th>Email:</th><td>" + str(email) + "</td></tr>"        
        
        # htmlCabecera += "</table>"
        
                
        #Cabecera proyecto
        # htmlCabecera += "<table class='table_wo'>"

        

        # decorators = ProyectDecorator.objects.filter(proyects = wo.proyect)

        # if decorators and 1 == 2:

        #     htmlCabecera += "<tr><th rowspan='" + str(len(decorators)) + "' style='width: 85px; text-align: left; vertical-align: top;'>Decorator:</th>"
        #     n = 0

        #     for decorator in decorators:
        #         name = decorator.name if str(decorator.name) != "" else "--"
        #         phone = decorator.phone if str(decorator.phone) != "" else "--"
        #         email = decorator.email if str(decorator.email) != "" else "--"

        #         if n == 0:
        #             htmlCabecera += "<td>" + str(name) + " / " + str(phone) + " / " + str(email) + "</td>"
        #             htmlCabecera += "</tr>"
        #             n+=1
        #         else:
        #             htmlCabecera += "<tr><td>" + str(name) + " / " + str(phone) + " / " + str(email) + "</td></tr>"            

        # htmlCabecera += "</table>"

        #Items


        #Cabecera proyecto

        items = Item.objects.filter(workorder = wo).order_by("id")                        
                
        if items and 1 == 2:
            
            n = 1
            
            for item in items:

                #htmlCabecera += " <div class='new-page'><table class='table_item'>"
                htmlCabecera += "<div><table class='table_item'>"
                htmlCabecera += "<tr><th colspan='2' style='background-color:#f1f1f1; border:1px solid'>Item: " + str(code) + "-" + str(n) + "</th></tr>"
                htmlCabecera += "</table></div>"


                n+=1

                category = item.subcategory.category.name if str(item.subcategory.category.name) != "" else "--"
                
                subcategory = "--"
                if item.subcategory.name:
                    subcategory = item.subcategory.name if str(item.subcategory.name) != "" else "--"
                
                group = "--"
                if item.group:
                    group = item.group.name if str(item.group.name) != "" else "--"
                
                place = "--"
                if item.place:
                    place = item.place.name if str(item.place.name) != "" else "--"
                
                
                qty = item.qty if str(item.qty) != "" else "--"

                
                
                
                date_end = "--"
                responsible = " "


                calendar = CalendarItem.objects.filter(item = item).first()

                if calendar:

                    if calendar.responsible:
                        responsible = calendar.responsible.name

                    if calendar.date_start:
                        if calendar.allday:
                            date_end = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y')
                        else:
                            date_end = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y %I:%M %p')

                notes = item.notes if str(item.notes) != "" else "--"


                htmlCabecera1 = "<table class='table_item_detalle'>"
                htmlCabecera1 += "<tr><th colspan='6' style='text-align: center;'><h1>" + str(category) + "</h1></th></tr>"
                htmlCabecera1 += "<tr><th>Sub Category:</td><td>" + str(subcategory) + "</td><th>Group:</th><td>" + str(group) + "</td><th>Place:</th><td>" + str(place) + "</td></tr>"
                htmlCabecera1 += "<tr style='height:5px'><th></th></tr>"
                htmlCabecera1 += "<tr><th>QTY:</th><td>" + str(qty) + "</td><th>Due date:</th><td>" + str(date_end) + "</td><th>Responsible:</th><td>" + str(responsible) + "</td></tr>"                
                htmlCabecera1 += "<tr style='height:5px'><th></th></tr>"
                htmlCabecera1 += "<tr><th style='vertical-align: top;'>Notes:</th><td colspan=3>" + str(notes) + "</td></tr>"
                htmlCabecera1 += "<tr style='height:5px'><th></th></tr>"
                

                attributes = ItemAttribute.objects.filter(item = item)
                # htmlCabecera2 = ""
                atributos1 = ''
                atributos2 = ''

                if attributes:
                    # htmlCabecera2 = "<table class='table_item_detalle'>"

                    for attribute in attributes:
                                                
                        atributteOptions = ItemAttributeNote.objects.filter(itemattribute = attribute)

                        if atributteOptions:
                            
                            name = attribute.attribute.name if str(attribute.attribute.name) != "" else "--"
                            atributos2 += "<tr><th valign='top'>" + str(name) + ":</th><td colspan=5>"
                            atributos2 += "<table class='tabla_atributo_opciones'>"
                            atributos2 += "<tr>"

                            tds = 0

                            for option in atributteOptions:
                                tds += 1
                                notes = option.attributeoption.name if str(option.attributeoption.name) != "" else "--"
                                atributos2 += "<td valign='middle'>" + str(notes) + "</td><td>"
                                
                                if option.attributeoption.file:
                                    atributos2 += "<img src='media/" + str(option.attributeoption.file.name) + "'width='80%'/>"
                                
                                atributos2 += '</td>'


                                if tds == 2:
                                    tds = 0
                                    atributos2 += "</tr><tr>"

                            atributos2 += "</tr></table>"
                            atributos2 += "</td></tr>"


                        else:                            

                            name = attribute.attribute.name if str(attribute.attribute.name) != "" else "--"
                            notes = attribute.notes if str(attribute.notes) != "" else "--"
                            atributos1 += "<tr><th>" + str(name) + ":</th><td colspan=3>" + str(notes) + "</td></tr>"
                            atributos1 += "<tr style='height:5px'><th></th></tr>"                            

                                    
                    htmlCabecera1 += atributos1 + atributos2
                    
                    # htmlCabecera2 += "</table>"


                # htmlCabecera += "<tr><th style='padding:0 0; text-align: left; vertical-align: top;'>" + htmlCabecera1 + "</th><th style='padding:0 0; text-align: left; vertical-align: top;'>" + htmlCabecera2 + "</th></tr>"

                htmlCabecera1 += "</table>"
                htmlCabecera += htmlCabecera1

            
                materials= ItemMaterial.objects.filter(item = item).order_by('id')

                htmlCabeceraMat = ""
                htmlCabeceraImg = ""

                if materials:
                    
                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td colspan='3' style='background-color:#f1f1f1'><b>Materials:</b></td></tr>"                    
                    table_img = ""
                    nt = 1

                    htmlCabeceraMat += "<table><tr><td style='width:300px; border-left:none; border-top:none'></td><td style='width:170px'>QTY</td><td style='width:170px'>Received QTY</td><td style='width:100px'>Received Date</td></tr>"
                    
                    for material in materials:

                        materialName = str(material.notes)
                        qty = str(material.qty)   
                        qtyR = ''             
                        dateR = ''

                        if material.qty_received:
                            qtyR = material.qty_received

                        if material.date_received:                            
                            dateR = material.date_received

                        htmlCabeceraMat += '<tr><td>' + materialName + '</td>' 
                        htmlCabeceraMat += '<td>' + qty + '</td>' 
                        htmlCabeceraMat += '<td>' + qtyR + '</td>'
                        htmlCabeceraMat += '<td>' + dateR + '</td>'

                        htmlCabeceraMat += '</tr>'
                    
                    htmlCabeceraMat += "</table><br/>"                     
                    htmlCabecera += htmlCabeceraMat
                    
                
                    
                    for material in materials:
                        file = material.file.name if str(material.file.name) != "" else "--"
                        notes = material.notes if str(material.notes) != "" else "--"
                        
                        table_img = "<table><tr><td style='padding:0 0; text-align: center; vertical-align: top; height=180px'><img src='media/" + file + "'width='90%'/></td></tr><tr><td style='text-align: left; vertical-align: top;'>" + notes + "</td></tr></table>"                                                
                        
                        if material.file:
                            if material.file.url[-4:] not in ('.pdf','.doc','.xls','.ppt') and material.file.url[-5:] not in ('.docx','.xlsx','.pptx'):
                                if nt == 1:
                                    htmlCabeceraImg += "<tr><td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                                elif nt == 2:
                                    htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                                elif nt == 3:
                                    htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td></tr>"
                                    nt = 0
                            
                                nt += 1
                    
                    htmlCabecera += htmlCabeceraImg

                    htmlCabecera += "</table>"


                images= ItemImage.objects.filter(item = item)

                if images:
                    
                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td colspan='3' style='background-color:#f1f1f1'><b>Images:</b></td></tr>"
                    htmlCabeceraImg = ""
                    table_img = ""
                    nt = 1
                    for image in images:
                        file = image.file.name if str(image.file.name) != "" else "--"
                        notes = image.notes if str(image.notes) != "" else "--"
                        table_img = "<table><tr><td style='padding:0 0; text-align: center; vertical-align: top; height=180px'><img src='media/" + file + "'width='90%'/></td></tr><tr><td style='text-align: left; vertical-align: top;'>" + notes + "</td></tr></table>"                                                
                        if nt == 1:
                            htmlCabeceraImg += "<tr><td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                        elif nt == 2:
                            htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                        elif nt == 3:
                            htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td></tr>"
                            nt = 0
                        
                        nt += 1
                    
                    htmlCabecera += htmlCabeceraImg

                    htmlCabecera += "</table>"



                if wo.description and wo.description.strip() != '':

                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td style='background-color:#f1f1f1'><b>Notes:</b></td></tr>"
                    htmlCabecera += "<tr><td>" + wo.description + "</td></tr>"
                    htmlCabecera += "</table>"
            


                



    template = get_template('proyect/pdf_template.html')
    context = {
        'CABECERA': htmlCabecera,
        'URL': settings.BASE_DIR,
        # 'MEDIA_URL': settings.MEDIA_URL
    }
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="WorkOrder_{}.pdf"'.format(workorderId)

    pisa_status = pisa.CreatePDF(io.StringIO(html), 
                    dest=response,
                    link_callback=link_callback) 

    if pisa_status.err:
        return HttpResponse('Error generando el PDF', status=500)
    
    return response




def link_callback(uri, rel):
    """
    Convierte URIs en rutas absolutas para xhtml2pdf
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # por ejemplo: /static/
        sRoot = settings.STATIC_ROOT      # por ejemplo: /var/www/static/
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # deja la URI como está si no se puede procesar

    if not os.path.isfile(path):
        raise Exception('Archivo no encontrado: %s' % path)
    return path