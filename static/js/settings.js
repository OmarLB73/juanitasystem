"use strict";
var KTProjectSettings = {
    init: function () {
        !function () {
            var t;            
            $("#kt_datepicker_1").flatpickr({ enableTime: !0, dateFormat: "Y-m-d, H:i" });
            var e = document.getElementById("projFormNew"),
                i = e.querySelector("#btnSave");
            t = FormValidation.formValidation(e, {
                fields: {
                    address: { validators: { notEmpty: { message: " " } } },
                    customerName: { validators: { notEmpty: { message: " " } } }                                     
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


                    var message = $('#alertSave').val();
                    var message2 = $('#alertInfoRequired').val();


                    e.preventDefault(),
                        t.validate().then((function (t) {                            
                            "Valid" == t ?                            
                                swal.fire({
                                    title: '¿Are you sure?',
                                    text: message,
                                    icon: 'info',
                                    showCancelButton: true,
                                    confirmButtonText: 'Yes',
                                    cancelButtonText: 'Cancel'
                                }).then((result) => {
                                    if (result.isConfirmed) {                                                                                
                                        // Si el usuario confirma, enviar el formulario      
                                        
                                        $('#projFormNew')[0].submit(); // Enviar el formulario manualmente
                                        
                                        // var exist = $('#proyectExist').val();

                                        // if(exist != ""){
                                        
                                        //     swal.fire({
                                        //         text: "The address already exists! Please review the projects.",
                                        //         icon: "error",
                                        //         buttonsStyling: !1,
                                        //         confirmButtonText: "Ok!",
                                        //         customClass: { confirmButton: "btn fw-bold btn-light-primary" }
                                        //     }).then((result) => {
                                        //         if (result.isConfirmed) {
                                        //             $('html, body').animate({ scrollTop: 0 }, 'fast');
                                        //         }
                                        //     });
                                        // }
                                        // else{
                                        //     $('#btnSave')[0].submit(); // Enviar el formulario manualmente
                                        // }                                        
                                        
                                    } else {
                                        // Si el usuario cancela, no hacer nada
                                        console.log('Form not sent');
                                    }
                                })                                                                                                                                                                                            
                                : swal.fire({
                                    text: message2,
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
