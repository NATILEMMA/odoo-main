odoo.define('auth_signup_verify_email.portal_new', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const {_t, qweb} = require('web.core');

    publicWidget.registry.portalProduct = publicWidget.Widget.extend({

        selector: '#partner_product',
        read_events: {
            'change select[name="product_id"]': '_basedOnPortal',
        },

        init: function () {
             this._super.apply(this, arguments);
         },

         start: function () {
             var self = this;
         },

        _basedOnPortal: function() {
            this.$product = this.$('select[name="product_id"]');
            this.$prod = this.$product.find(':selected').attr('data_product_price');
            if (this.$prod) {
              $('.price_add').text(`Membership Price: ${this.$prod}`);
            } else {
              $('.price_add').text(`Membership Price: 0.0`);
            }
        },
    });

    publicWidget.registry.registrationDetails = publicWidget.Widget.extend({

        selector: '.registration_details',
        read_events: {
            'change select[name="subcity_id"]': '_subcityChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$wereda = this.$('select[name="wereda_id"]');
            this.$weredaOptions = this.$wereda.filter(':enabled').find('option:not(:first)');
            this._weredaChange();
            return def;
         },

         _weredaChange: function() {
             var $subcity = this.$('select[name="subcity_id"]');
             var subcityID = ($subcity.val() || 0);
             this.$weredaOptions.detach();
             var $displayedState = this.$weredaOptions.filter('[data-parent_id=' + subcityID + ']');
             var nb = $displayedState.appendTo(this.$wereda).show().length;
             this.$wereda.parent().toggle(nb >= 1);
         },

         _subcityChange: function() {
             this._weredaChange();
         },
    });

    publicWidget.registry.registrationDetailsOnPortal = publicWidget.Widget.extend({

        selector: '.o_portal_details',
        read_events: {
            'change select[name="subcity_id"]': '_subcityChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$wereda = this.$('select[name="wereda_id"]');
            this.$weredaOptions = this.$wereda.filter(':enabled').find('option:not(:first)');
            this._weredaChange();
            return def;
         },

         _weredaChange: function() {
             var $subcity = this.$('select[name="subcity_id"]');
             var subcityID = ($subcity.val() || 0);
             this.$weredaOptions.detach();
             var $displayedState = this.$weredaOptions.filter('[data-parent_id=' + subcityID + ']');
             var nb = $displayedState.appendTo(this.$wereda).show().length;
             this.$wereda.parent().toggle(nb >= 1);
         },

         _subcityChange: function() {
             this._weredaChange();
         },
    });
});
