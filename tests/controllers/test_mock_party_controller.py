import unittest

from response_operations_ui.controllers import mock_party_controller

example_data = [
    {'firstName': 'Jillayne', 'lastName': 'Tran', 'emailAddress': 'jtran0@simplemachines.org'},
    {'firstName': 'Virgie', 'lastName': 'Wiley', 'emailAddress': 'vwiley2@bing.com'},
    {'firstName': 'Alikee', 'lastName': 'Banton', 'emailAddress': 'abanton1@dell.com'},
    {'firstName': 'Tulley', 'lastName': 'Butts', 'emailAddress': 'tbutts3@google.pl'},
    {'firstName': 'Mollie', 'lastName': 'Singyard', 'emailAddress': 'msingyard4@cargocollective.com'},
    {'firstName': 'Mead', 'lastName': 'Wakefield', 'emailAddress': 'mwakefield5@ucoz.com'},
    {'firstName': 'Hildegaard', 'lastName': 'Kubik', 'emailAddress': 'hkubik6@cmu.edu'},
    {'firstName': 'Ami', 'lastName': 'Brimble', 'emailAddress': 'abrimble7@nasa.gov'},
    {'firstName': 'Sidonia', 'lastName': 'Piddle', 'emailAddress': 'spiddle8@sakura.ne.jp'},
    {'firstName': 'Raquela', 'lastName': 'Grzelewski', 'emailAddress': 'rgrzelewski9@mlb.com'},
    {'firstName': 'Gerry', 'lastName': 'Tidbold', 'emailAddress': 'gtidbolda@bluehost.com'},
    {'firstName': 'Cammy', 'lastName': 'Childerley', 'emailAddress': 'cchilderleyb@google.es'},
    {'firstName': 'Sutherland', 'lastName': 'Barrett', 'emailAddress': 'sbarrettc@symantec.com'},
    {'firstName': 'August', 'lastName': 'Moss', 'emailAddress': 'amossd@hubpages.com'},
    {'firstName': 'Gualterio', 'lastName': 'Armsden', 'emailAddress': 'garmsdene@nifty.com'},
    {'firstName': 'Garnette', 'lastName': 'Harrie', 'emailAddress': 'gharrief@netvibes.com'},
    {'firstName': 'Zelda', 'lastName': 'Hale', 'emailAddress': 'zhaleg@paginegialle.it'},
    {'firstName': 'Kathryn', 'lastName': 'Goose', 'emailAddress': 'kgooseh@tmall.com'},
    {'firstName': 'Daisy', 'lastName': 'Roddan', 'emailAddress': 'droddani@smh.com.au'},
    {'firstName': 'Magda', 'lastName': 'Hussey', 'emailAddress': 'mhusseyj@imgur.com'},
    {'firstName': 'Fan', 'lastName': 'Wiggam', 'emailAddress': 'fwiggamk@theatlantic.com'},
    {'firstName': 'Hadleigh', 'lastName': 'Duffyn', 'emailAddress': 'hduffynl@buzzfeed.com'},
    {'firstName': 'Kelby', 'lastName': 'Dimblebee', 'emailAddress': 'kdimblebeem@ask.com'},
    {'firstName': 'Torrey', 'lastName': 'Palin', 'emailAddress': 'tpalinn@technorati.com'},
    {'firstName': 'Malinde', 'lastName': 'Featley', 'emailAddress': 'mfeatleyo@oakley.com'},
    {'firstName': 'Chico', 'lastName': 'Thrasher', 'emailAddress': 'cthrasherp@cbc.ca'},
    {'firstName': 'Thorvald', 'lastName': 'Puleston', 'emailAddress': 'tpulestonq@latimes.com'},
    {'firstName': 'Hendrick', 'lastName': 'Pollins', 'emailAddress': 'hpollinsr@sfgate.com'},
    {'firstName': 'Lyn', 'lastName': 'MacGaughie', 'emailAddress': 'lmacgaughies@webnode.com'},
    {'firstName': 'Patrick', 'lastName': 'Mothersdale', 'emailAddress': 'pmothersdalet@istockphoto.com'}
]


class TestMockPartyController(unittest.TestCase):

    def setup(self):
        pass

    # First name search testing

    # Matches only one by searching for a complete first name unique within the data
    def test_filter_by_first_name_with_valid_complete_input(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, 'Zelda', '', '')

        self.assertListEqual(output, [
                             {
                                 'firstName': 'Zelda',
                                 'lastName': 'Hale',
                                 'emailAddress': 'zhaleg@paginegialle.it'
                             }
                             ],
                             'Filtering by complete first name did not return correct entry')

    # Matches many outputs by specifying only an uppercase M in first name.  Should match 4, as 4 start with m.
    def test_filter_by_first_name_with_valid_partial_input_in_capitals(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, 'M', '', '')

        self.assertListEqual(output,
                             [
                                 {'firstName': 'Mollie', 'lastName': 'Singyard',
                                  'emailAddress': 'msingyard4@cargocollective.com'},
                                 {'firstName': 'Mead', 'lastName': 'Wakefield', 'emailAddress': 'mwakefield5@ucoz.com'},
                                 {'firstName': 'Magda', 'lastName': 'Hussey', 'emailAddress': 'mhusseyj@imgur.com'},
                                 {'firstName': 'Malinde', 'lastName': 'Featley', 'emailAddress': 'mfeatleyo@oakley.com'}
                             ],
                             'Did not return correct output for a uppercase partial input')

    # Matches many outputs by specifying only an lowercase m in first name.  Should match 4, as 4 start with m.
    def test_filter_by_first_name_with_valid_partial_input_in_lowercase(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, 'm', '', '')

        self.assertListEqual(output,
                             [
                                 {'firstName': 'Mollie', 'lastName': 'Singyard',
                                  'emailAddress': 'msingyard4@cargocollective.com'},
                                 {'firstName': 'Mead', 'lastName': 'Wakefield', 'emailAddress': 'mwakefield5@ucoz.com'},
                                 {'firstName': 'Magda', 'lastName': 'Hussey', 'emailAddress': 'mhusseyj@imgur.com'},
                                 {'firstName': 'Malinde', 'lastName': 'Featley', 'emailAddress': 'mfeatleyo@oakley.com'}
                             ],
                             'Did not return correct output for a lowercase partial input')

    # Matches no one, should return empty list.
    def test_filter_by_first_name_with_invalid_input(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, 'Dave', '', '')
        self.assertListEqual(output, [], 'Did not return empty list for a first name not present in list.')

    # Matches only one by searching for a complete first name unique within the data
    def test_filter_by_last_name_with_valid_complete_input(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', 'Wakefield', '')

        self.assertListEqual(output, [
                             {
                                 'firstName': 'Mead',
                                 'lastName': 'Wakefield',
                                 'emailAddress': 'mwakefield5@ucoz.com'
                             }
                             ],
                             'Filtering by complete last name did not return correct entry')

    # Matches many outputs by specifying only an uppercase T in last name.  Should match 4, as 4 start with m.
    def test_filter_by_last_name_with_valid_partial_input_in_capitals(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', 'T', '')

        self.assertListEqual(output,
                             [
                                 {'firstName': 'Jillayne', 'lastName': 'Tran',
                                  'emailAddress': 'jtran0@simplemachines.org'},
                                 {'firstName': 'Gerry', 'lastName': 'Tidbold',
                                  'emailAddress': 'gtidbolda@bluehost.com'},
                                 {'firstName': 'Chico', 'lastName': 'Thrasher', 'emailAddress': 'cthrasherp@cbc.ca'},
                             ],
                             'Did not return correct output for a uppercase partial input')

    # Matches many outputs by specifying only an lowercase t in last name.  Should match 4, as 4 start with m.
    def test_filter_by_last_name_with_valid_partial_input_in_lowercase(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', 't', '')

        self.assertListEqual(output,
                             [
                                 {'firstName': 'Jillayne', 'lastName': 'Tran',
                                  'emailAddress': 'jtran0@simplemachines.org'},
                                 {'firstName': 'Gerry', 'lastName': 'Tidbold',
                                  'emailAddress': 'gtidbolda@bluehost.com'},
                                 {'firstName': 'Chico', 'lastName': 'Thrasher',
                                  'emailAddress': 'cthrasherp@cbc.ca'},
                             ],
                             'Did not return correct output for a lowercase partial input')

    # Matches no one, should return empty list.
    def test_filter_by_last_name_with_invalid_input(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', 'Jenkins', '')
        self.assertListEqual(output, [], 'Did not return empty list for a first name not present in list.')

    def test_filter_by_email_with_complete_match(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', '', 'kgooseh@tmall.com')
        self.assertListEqual(output,
                             [{'firstName': 'Kathryn', 'lastName': 'Goose', 'emailAddress': 'kgooseh@tmall.com'}],
                             'Did not return correct match for exact email address')

    def test_filter_by_email_with_partial_lowercase_match(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', '', 'ee')
        self.assertListEqual(output, [
            {'firstName': 'Hadleigh', 'lastName': 'Duffyn', 'emailAddress': 'hduffynl@buzzfeed.com'},
            {'firstName': 'Kelby', 'lastName': 'Dimblebee', 'emailAddress': 'kdimblebeem@ask.com'},
        ], 'Did not return correct output for partial lowercase email')

    def test_filter_by_email_with_partial_uppercase_match(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', '', 'EE')
        self.assertListEqual(output, [
            {'firstName': 'Hadleigh', 'lastName': 'Duffyn', 'emailAddress': 'hduffynl@buzzfeed.com'},
            {'firstName': 'Kelby', 'lastName': 'Dimblebee', 'emailAddress': 'kdimblebeem@ask.com'},
        ], 'Did not return correct output for partial uppercase email')

    def test_filter_by_email_with_non_match(self):
        output = mock_party_controller.filter_json_by_passed_parameters(example_data, '', '', 'xx')
        self.assertListEqual(output, [], 'Did not return correct output for non-matching email')
