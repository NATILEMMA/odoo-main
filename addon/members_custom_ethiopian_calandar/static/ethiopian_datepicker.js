console.log("##### Ethiopian Calander Widget####")
odoo.define("EthiopianCalendar.EthiopianCalendarWidget", function(require){
    "use strict";
    var core = require('web.core');
    var time = require('web.time');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var _t = core._t;
    var qweb = core.qweb;
    var config = require('web.config');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var view_dialogs = require('web.view_dialogs');
    var widget_registry = require("web.widget_registry");
    var rpc = require('web.rpc')
    let clicked_val = 0
    
    var EthiopianCalendarWidget = Widget.extend({
                template: 'ethiopian_calander_widget',
                
                events:{},
            
            start: function() {
                var def = new $.Deferred();
                let picked_date = [];
                this._super();
                // this.$input = this.$('input.o_datepicker_input');
                console.log("##########",this)
                var self = this;
                $(function() {
                    var calendar = $.calendars.instance('ethiopian','am');
                    $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect: showDate});
                    // var pickeddate = showDate
                    // picked_date = showDate(date)
                    // console.log("pickedate",picked_date)
                });

                async function showDate(date) {
                    console.log("Mainfeedback",date)
                    let pickeddate = {
                    "day" : date[0]._day,
                    "month" : date[0]._month,
                    "year":date[0]._year
                    }

//                   

                }
            },
         
        
            
        });

        widget_registry.add('ethiopian_calander_widget', EthiopianCalendarWidget)


        var EthiopianCalendarWidget = Widget.extend({
            template: 'ethiopian_calander_widget',
            
            events:{},
        
        start: function() {
            var def = new $.Deferred();
            let picked_date = [];
            this._super();
            // this.$input = this.$('input.o_datepicker_input');
            console.log("##########",this)
            var self = this;
            $(function() {
                var calendar = $.calendars.instance('ethiopian','am');
                $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect: showDate});
                // var pickeddate = showDate
                // picked_date = showDate(date)
                // console.log("pickedate",picked_date)
            });

            async function showDate(date) {
                console.log("Mainfeedback",date)
                let pickeddate = {
                "day" : date[0]._day,
                "month" : date[0]._month,
                "year":date[0]._year
                }

//                   

            }
        },
     
    
        
    });

    widget_registry.add('ethiopian_calander_widget_three', EthiopianCalendarWidget)



        

});



