"use strict";
var KTProjectSettings = {
    init: function () {
        !function () {
            var t;            
            $("#kt_datepicker_1").flatpickr({ enableTime: !0, dateFormat: "Y-m-d, H:i" });
            var e = document.getElementById("kt_project_settings_form"),
                i = e.querySelector("#kt_project_settings_submit");
            t = FormValidation.formValidation(e, {
                fields: {
                    address: { validators: { notEmpty: { message: "Address is required" } } },
                    customerName: { validators: { notEmpty: { message: "Name is required" } } },
                    date: { validators: { notEmpty: { message: "Date is required" } } },                    
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    submitButton: new FormValidation.plugins.SubmitButton,
                    bootstrap: new FormValidation.plugins.Bootstrap5({ rowSelector: ".fv-row" })
                }
            }),
                i.addEventListener("click", (function (e) {
                    e.preventDefault(),
                        t.validate().then((function (t) {                            
                            "Valid" == t ?                            
                                swal.fire({
                                    title: '¿Are you sure?',
                                    text: 'Do you want to save the project?',
                                    icon: 'info',
                                    showCancelButton: true,
                                    confirmButtonText: 'Yes',
                                    cancelButtonText: 'Cancel'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        // Si el usuario confirma, enviar el formulario
                                        $('#kt_project_settings_form')[0].submit(); // Enviar el formulario manualmente
                                    } else {
                                        // Si el usuario cancela, no hacer nada
                                        console.log('Form not sent');
                                    }
                                })                                                                                                                                                                                            
                                : swal.fire({
                                    text: "Sorry, looks like there are some errors detected, please try again.",
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