odoo.define(function(require) {
                    "use strict";
                    var session = require('web.session');
                    var rpc = require('web.rpc')
                    let clicked_val = 0
                    console.log("clicked.....")
                    console.log('rpc', rpc)
                    console.log("THIS",self)
                    var current_url = window.location.href;
                    console.log("current_url",current_url)
                    var myArray = current_url.split("&");
                    var current_model = myArray[2].replace('model=',''); 
                    console.log("current model",current_model)
                    console.log("myArray[2]",myArray[2])
                    console.log('session',session)
                    var calendar = $.calendars.instance('ethiopian','am');
                    $('#DatepickerFour   ').calendarsPicker({calendar: calendar,onSelect:function()
                    {
                      var dateObject = $(this).calendarsPicker("getDate")
                      console.log("dateObject", dateObject)
                        let pickeddate = {
                                "day" : dateObject[0]._day,
                                "month" : dateObject[0]._month,
                                "year":dateObject[0]._year,
                                "current_model": current_model,
                                "url": current_url,
                                "pick": 4,


                                }   
                      var dd,model;
                      dd = current_url.split('model=')
                      model = dd[1].toString()
                      model = model.split('&')
                      rpc.query({
                                model: model[0],
                                method: 'date_convert_and_set',
                                args: [pickeddate],
                            })
                      
             

                    }});
                });