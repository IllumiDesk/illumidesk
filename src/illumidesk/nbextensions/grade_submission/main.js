define([
    'base/js/namespace'
    ], function(
        Jupyter
    ) {
        'use strict';

        // Get url from browser's address bar
        var get_url = function () {
            var proto = window.location.protocol;                        
            return proto + "//" + window.location.host + "/hello";
        }

        var submit_assignment = function () {
            
            var submit_url = get_url()
            fetch(submit_url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json;charset=utf-8' },
                referrerPolicy: 'no-referrer'
            }).then(function (response) {
                if (!response.ok) {
                    alert('Error: there was an error processing your grades submission request.')
                    return;
                }
                else {
                    alert("Success: your assignment grades has been successfully submitted.")
                }
            })
        }

        // Submit assignment button
        var submit_assignment_button = function () {
            Jupyter.toolbar.add_buttons_group([
                Jupyter.keyboard_manager.actions.register ({
                    'help': 'Submit assignment',
                    'icon' : 'fa-paper-plane',
                    'handler': submit_assignment
                },  'add-default-cell', 'Default cell')
            ])
        }

        // Run on start
        function load_ipython_extension() {
            submit_assignment_button();
        }

        return {
            load_ipython_extension: load_ipython_extension
        };
});
