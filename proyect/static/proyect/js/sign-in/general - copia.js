"use strict";
var KTSigninGeneral = function () {
    var t, e, i;
    return {
        init: function () {
            t = document.querySelector("#loginForm"),
                e = document.querySelector("#buttonSubmit"),
                i = FormValidation.formValidation(t, {
                    fields: {
                        email: {
                            validators: {
                                notEmpty:
                                    { message: "Email address is required" }, emailAddress:
                                    { message: "The value is not a valid email address" }
                            }
                        },
                        password: {
                            validators: {
                                notEmpty:
                                    { message: "The password is required" }
                            }
                        }
                    },
                    plugins: { trigger: new FormValidation.plugins.Trigger, bootstrap: new FormValidation.plugins.Bootstrap5({ rowSelector: ".fv-row" }) }
                }),
                e.addEventListener("click", (function (n) {
                    n.preventDefault(),
                        i.validate().then((function (i) {
                            "Valid" == i ? (
                                e.setAttribute("data-kt-indicator", "on"),
                                e.disabled = !0,
                                setTimeout((function () {
                                    var $form = $('#loginForm');
                                    var url_validate = document.querySelector("#url_validate").value;
                                    $.ajax({
                                        url: url_validate,
                                        type: 'POST',
                                        data: $form.serialize(), // Serializa los datos del formulario
                                        success: function (response) {
                                            if (response.is_valid) {                                                
                                                Swal.fire({ text: response.message, icon: "success", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn btn-primary" }, }).then((function (e) { e.isConfirmed && (window.location.href = response.redirect_url ) }))
                                            }
                                            else{
                                                Swal.fire({ text: response.message, icon: "error", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn btn-primary" } })
                                            }
                                        },
                                        error: function (xhr, status, error) {
                                            Swal.fire({ text: "Communication error with the server. Please contact to system administrator.", icon: "error", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn btn-primary" } })
                                        }
                                    });
                                e.removeAttribute("data-kt-indicator"),
                                e.disabled = !1                                   
                                }), 2e3)) : Swal.fire({ text: "Sorry, looks like there are some errors detected, please try again.", icon: "error", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn btn-primary" } })
                        }))
                }))
        }
    }
}(); KTUtil.onDOMContentLoaded((function () { KTSigninGeneral.init() }));