console.log("##### Ethiopian Calander Widget####")
odoo.define("AmharicDatepickerCalendar.EthiopianCalendarWidget", function(require){
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
                // console.log("##########",this.$input)
                var self = this;
                $(function() {
                    console.log("clicked......")
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

                    picked_date.push(pickeddate)
                    console.log(picked_date)
                    let Postdate = await self._rpc({
                                model: 'res.partner',
                                // rout: `/get_order`,
                                method: 'date_convert_and_set',
                                args: [picked_date],
                            })
            

                } 
                
                console.log("VALue:",picked_date)    
            },
         
        
            
        });

        widget_registry.add('ethiopian_calander_widget', EthiopianCalendarWidget)


        

});





// console.log("##### Ethiopian Calander Widget####")
// odoo.define("AmharicDatepickerCalendar.EthiopianCalendarWidget", function(require){
//     "use strict";

//     var config = require('web.config');
//     var Widget = require('web.Widget');
//     var Dialog = require('web.Dialog');
//     var view_dialogs = require('web.view_dialogs');
//     var widget_registry = require("web.widget_registry");
//     var rpc = require('web.rpc')
//     let clicked_val = 0

//     console.log("####### loaded....")
  

//     var EthiopianCalendarWidget = Widget.extend({
//         template: 'ethiopian_calander_widget',
        
//         events:{},

//         init: function (parent, value) {
//             this.value = value.data;
//             console.log("-----------------")
//             this._super(parent);
//             console.log(this);
//         },
       
//         start: function(){
//             console.log("Starting function...")
            
//             let vals = this.value;
//             let self = this;
//             this.el.onclick = async function(ev){
//                 ev.preventDefault();
//                 console.log(" VALUES: ")
//                 console.log(this)
//                 console.log(vals)
//                 console.log(self)

//             //     var pickeddate = 0;
//             // $(function() {
//             //     console.log("clicked......")
//             //      var calendar = $.calendars.instance('ethiopian','am');
//             //     $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect: showDate});
//             //     var pickeddate = showDate
//             //     console.log("pickedate",pickeddate)
//             // });
            
//             // async function showDate(date) {
//             //     console.log("feedback",date)
//             //     var picked_date = {
//             //     "day" : date[0]._day,
//             //     "month" : date[0]._month,
//             //     "year":date[0]._year
//             //     }
            
//             //      console.log("POST DATE TO PYTHON ")
//             //     console.log(picked_date)
//             //      let Postdate = await self._rpc({
//             //         model: 'res.partner',
//             //         // rout: `/get_order`,
//             //         method: 'date_convert_and_set',
//             //         args: [picked_date],
//             //     })
                
//             // }


//             // var rpc = require('web.rpc')

//                 // rpc.query(

//                 //     model: //your model,

//                 //     method: //your method,

//                 //     args: [{

//                 //             'arg1': value1,

//                 //     }]

//                 //     }).then(function (result) { 

//                 //                 // your code 

//                 //                 });

                
                

//                 // let picked_date = {
//                 //     "year": pickeddate
//                 // }
//                 // console.log("POST DATE TO PYTHON ")
//                 // console.log(picked_date)
//                 // let Postdate = await self._rpc({
//                 //     model: 'res.partner',
//                 //     // rout: `/get_order`,
//                 //     method: 'date_convert_and_set',
//                 //     args: [picked_date],
//                 // })
//                 // console.log("RESPONSE INFO DATA: ")
//                 // console.log(Postdate)
                
//             }

           
            
//         },
       
       
        
//     });
//     widget_registry.add('ethiopian_calander_widget', EthiopianCalendarWidget)

  

// })






