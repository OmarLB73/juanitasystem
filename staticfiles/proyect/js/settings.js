"use strict";
var KTProjectSettings = {
    init: function () {
        !function () {
            var t; $("#kt_datepicker_1").flatpickr({enableTime: !0,dateFormat:"Y-m-d, H:i"});
            var e = document.getElementById("kt_project_settings_form"),
                i = e.querySelector("#kt_project_settings_submit");
            t = FormValidation.formValidation(e, {
                fields: {
                    name: { validators: { notEmpty: { message: "La dirección es requerida" } } },
                    type: { validators: { notEmpty: { message: "Project type is required" } } },
                    description: { validators: { notEmpty: { message: "La descripción es requerida" } } },
                    date: { validators: { notEmpty: { message: "La fecha es requerida" } } },
                    responsable: { validators: { notEmpty: { message: "El responsable es requeerido" } } },
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    submitButton: new FormValidation.plugins.SubmitButton,
                    bootstrap: new FormValidation.plugins.Bootstrap5({ rowSelector: ".fv-row" })
                }
            }),
                i.addEventListener("click", (function (e) { e.preventDefault(), t.validate().then((function (t) { "Valid" == t ? swal.fire({ text: "Thank you! You've updated your project settings", icon: "success", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn fw-bold btn-light-primary" } }) : swal.fire({ text: "Sorry, looks like there are some errors detected, please try again.", icon: "error", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn fw-bold btn-light-primary" } }) })) }))
        }()
    }
}; KTUtil.onDOMContentLoaded((function () { KTProjectSettings.init() }));
