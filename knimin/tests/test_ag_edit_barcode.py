# -*- coding: utf-8 -*-
from unittest import main

from tornado.escape import url_escape, xhtml_escape

from knimin.tests.tornado_test_base import TestHandlerBase
from knimin import db


class TestAGEditBarcodeHandler(TestHandlerBase):
    def test_get_not_authed(self):
        response = self.get('/ag_edit_barcode/')
        self.assertEqual(response.code, 200)
        port = self.get_http_port()
        self.assertEqual(response.effective_url,
                         'http://localhost:%d/login/?next=%s' %
                         (port, url_escape('/ag_edit_barcode/')))

    def test_get(self):
        self.mock_login_admin()

        # check that error is raised for unknown barcode
        response = self.get('/ag_edit_barcode/', {'barcode': 'unknown'})
        self.assertEqual(response.code, 500)

        # make sure return code 400 is returned, if barcode is not given
        response = self.get('/ag_edit_barcode/', {})
        self.assertEqual(response.code, 400)

        # check if page is rendered properly
        barcode = db.get_barcodes_with_results()[0]
        response = self.get('/ag_edit_barcode/', {'barcode': barcode})
        self.assertEqual(response.code, 200)
        details = db.getAGBarcodeDetails(barcode)
        l = db.search_kits(details['ag_kit_id'])[0]
        self.assertIn('name="barcode" id="barcode" value="%s"' %
                      barcode.encode('utf-8'), response.body)
        for s in db.human_sites:
            if details['site_sampled'] == str(s):
                self.assertIn('<option value="%s" selected>%s</option>' %
                              (str(s), str(s)), response.body)
            else:
                self.assertIn('<option value="%s">%s</option>' %
                              (str(s), str(s)), response.body)
        for e in db.general_sites:
            if details['environment_sampled'] == str(e):
                self.assertIn('<option value="%s" selected>%s</option>' %
                              (str(e), str(e)), response.body)
            else:
                self.assertIn('<option value="%s">%s</option>' %
                              (str(e), str(e)), response.body)
        for p in db.getHumanParticipants(l) + db.getAnimalParticipants(l):
            if details['participant_name'] == p:
                self.assertIn('<option value="%s" selected>%s</option>' %
                              ((xhtml_escape(p), ) * 2), response.body)
            else:
                self.assertIn('<option value="%s" >%s</option>' %
                              ((xhtml_escape(p), ) * 2), response.body)

    def test_post(self):
        self.mock_login_admin()
        kit_id = '15d5baf0-0b50-40aa-bb78-4e527795017e'
        participant_name = db.ut_get_participant_names_from_ag_login_id(
            db.search_kits(kit_id)[0])[0]
        response = self.post('/ag_edit_barcode/',
                             {'barcode': '000023299',
                              'ag_kit_id': kit_id,
                              'site_sampled': 'Stool',
                              'sample_date': '2015-01-17',
                              'sample_time': '08:00:00',
                              'participant_name': participant_name,
                              'notes': "REMOVED",
                              'refunded': 'N',
                              'withdrawn': 'N',
                              })
        self.assertEqual(response.code, 400)

        response = self.post('/ag_edit_barcode/',
                             {'barcode': '000023299',
                              'ag_kit_id': kit_id,
                              'site_sampled': 'Stool',
                              'sample_date': '2015-01-17',
                              'sample_time': '08:00:00',
                              'participant_name': participant_name,
                              'notes': "REMOVED",
                              'refunded': 'N',
                              'withdrawn': 'N',
                              'environment_sampled': None,
                              })
        self.assertEqual(response.code, 200)
        self.assertIn("Barcode was updated successfully", response.body)

        response = self.post('/ag_edit_barcode/',
                             {'barcode': '0000',
                              'ag_kit_id': 'notInDB',
                              'site_sampled': 'Stool',
                              'sample_date': '2015-01-17',
                              'sample_time': '08:00:00',
                              'participant_name': participant_name,
                              'notes': "REMOVED",
                              'refunded': 'N',
                              'withdrawn': 'N',
                              'environment_sampled': None,
                              })
        # TODO: think about returning a non-OK status code to better report
        # this error, see issue #139
        self.assertEqual(response.code, 200)
        self.assertIn("Error Updating Barcode Info", response.body)


if __name__ == "__main__":
    main()
