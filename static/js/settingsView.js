"use strict";
var KTProjectSettings = {
    init: function () {
        !function () {
            var t;            
            // $("#kt_datepicker_1").flatpickr({ enableTime: !0, dateFormat: "Y-m-d, H:i" });
            var e = document.getElementById("formItem"),
                i = e.querySelector("#submitItem");
            t = FormValidation.formValidation(e, {
                fields: {
                    category: { validators: { notEmpty: { message: " " } } },
                    subcategory: { validators: { notEmpty: { message: " " } } },
                    group: { validators: { notEmpty: { message: " " } } },
                    place: { validators: { notEmpty: { message: " " } } },
                    qty: { validators: { notEmpty: { message: " " } } },
                    date_proposed: { validators: { notEmpty: { message: " " } } },
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    submitButton: new FormValidation.plugins.SubmitButton,
                    bootstrap: new FormValidation.plugins.Bootstrap5({ rowSelector: ".fv-row" })
                }
            }),
                i.addEventListener("click", (function (e) {

                    document.querySelectorAll('.fv-help-block').forEach(function(message) {
                        message.style.display = 'none'; // Oculta los mensajes de error
                    });                    

                    e.preventDefault(),
                        t.validate().then((function (t) {
                            "Valid" == t ?                            
                                swal.fire({
                                    title: '¿Are you sure?',
                                    text: 'Do you want to save the item?',
                                    icon: 'info',
                                    showCancelButton: true,
                                    confirmButtonText: 'Yes',
                                    cancelButtonText: 'Cancel'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        // Si el usuario confirma, enviar el formulario
                                        // $('#formItem')[0].submit(); // Enviar el formulario manualmente

                                        var hasContent = false;   
                                        var rows = document.querySelectorAll("#tableMaterials tbody tr");                                                                                                                    
                                        // Recorrer todas las filas
                                        for (var y = 0; y < rows.length; y++) {
                                            // Obtener todos los campos de input dentro de la fila
                                            var inputs = rows[y].querySelectorAll('input.autocompleteMaterial');
    
                                            // Verificar si alguno de los inputs tiene un valor
                                            
                                            inputs.forEach(function(input) {
                                                if (input.value.trim() !== "") {  // Verifica si el valor del input no está vacío
                                                    hasContent = true;
                                                }
                                            });

                                            var fileInput = rows[y].querySelector('input[type="file"]');
                                            var hiddenInput = rows[y].querySelector('input[type="hidden"]');

                                            hiddenInput.value = fileInput.files.length > 0 ? 1 : 0;
                                            
                                        }
                                        
                                        var rows = document.querySelectorAll("#tableImages tbody tr");                                        
                                        for (var y = 0; y < rows.length; y++) {
                                            var fileInput = rows[y].querySelector('input[type="file"]');
                                            var hiddenInput = rows[y].querySelector('input[type="hidden"]');

                                            hiddenInput.value = fileInput.files.length > 0 ? 1 : 0;
                                            
                                        }
    
                                        if(!hasContent){                                        
                                            $('#messageMaterial').show();
                                            $('#messageMaterial').html('<div class="alert alert-warning alert-dismissible fade show" role="alert">You must enter materials.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');                                        
                                        }
                                        else{
                                            $('#messageMaterial').html('');
                                            $('#messageMaterial').fadeOut();
                                                                                        
                                            i.setAttribute("data-kt-indicator", "on");
                                            i.disabled = true;  // Deshabilitar el botón mientras el proceso se realiza
                                            
                                        
                                            // var formData = $('#formItem').serialize(); // Serializa los datos del formulario
                                            var formData = new FormData();  // Creamos un objeto FormData vacío

                                            // Serializamos los datos del formulario (excepto los archivos)
                                            var serializedData = $('#formItem').serialize(); 

                                            // Convertimos los datos serializados en un objeto y lo agregamos al FormData
                                            var params = serializedData.split('&');
                                            params.forEach(function(param) {
                                                var keyValue = param.split('=');
                                                var key = decodeURIComponent(keyValue[0]);
                                                var value = decodeURIComponent(keyValue[1] || '');
                                                formData.append(key, value);
                                            });

                                            // Seleccionamos todos los inputs de tipo file
                                            $('input[type="file"]').each(function() {
                                                var input = $(this)[0]; // Obtener el campo de archivo actual
                                                var inputName = input.name; // Obtenemos el nombre del campo (images1, images2, images3, etc.)

                                                // Verificamos si hay archivos seleccionados
                                                if (input.files.length > 0) {
                                                    // Iteramos sobre los archivos seleccionados
                                                    for (var i = 0; i < input.files.length; i++) {
                                                        // Agregamos el archivo al FormData usando el nombre del input como clave
                                                        formData.append(inputName, input.files[i]);
                                                    }
                                                }
                                            });
                                            
                                            $.ajax({
                                                type: "POST",
                                                url: "../../saveItem/",  // Reemplaza con la URL de tu vista
                                                data: formData,
                                                processData: false,  // Esto es importante para enviar archivos correctamente
                                                contentType: false,  // Evitar que jQuery configure el tipo de contenido automáticamente
                                                beforeSend: function(xhr, settings) {
                                                    // Añadir el token CSRF en las cabeceras
                                                    xhr.setRequestHeader('X-CSRFToken', $('meta[name="csrf-token"]').attr('content'));
                                                },
                                                success: function(response) {
                                                    loadWOs();
                                                    cleanItemForm();
                                                    // $('#nav-items-tab').click();

                                                    toastr.options = {
                                                        "closeButton": true,
                                                        "progressBar": true,
                                                        "positionClass": "toast-top-right",
                                                        "timeOut": "4000"
                                                    };
                
                                                    toastr.success("The item has been saved successfully!");
                                                    
                                                    // $('#messageSave').show();
                                                    // $('#messageSave').html('<div class="alert alert-success alert-dismissible fade show" role="alert">The <strong>item</strong> has been saved successfully.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
                                                    // setTimeout(function() {
                                                    //     $('#messageSave').fadeOut(); // Esto hará que el div se desvanezca
                                                    // }, 5000); 

                                                    $('#messageMaterial').html('');
                                                    $('#messageMaterial').fadeOut();
                                                    $('#modalItem').modal('hide');

                                                },
                                                error: function() {
                                                    console.error("Error server: " + error, event.error);
                                                }
                                            });

                                            i.setAttribute("data-kt-indicator", "off");
                                            i.disabled = false;  // Deshabilitar el botón mientras el proceso se realiza
                                        }

                                    } else {
                                        // Si el usuario cancela, no hacer nada
                                        console.log('Form not sent');
                                    }
                                })                                                                                                                                                                                            
                                : swal.fire({
                                    text: "Please complete the required information.",
                                    icon: "error",
                                    buttonsStyling: !1,
                                    confirmButtonText: "Ok, got it!",
                                    customClass: { confirmButton: "btn fw-bold btn-light-primary" }
                                })
                        }))
                }))
        }()
    }
}; KTUtil.onDOMContentLoaded((function () { KTProjectSettings.init() }));
