import unittest
from server import normalize, search

class SearchTests(unittest.TestCase):
    def test_metadata(self):
        record = normalize({'title':['<i>Strategy</i> &amp; change'], 'DOI':'10.1/abc',
                            'author':[{'given':'A', 'family':'Smith'}],
                            'published':{'date-parts':[[2024,2]]},
                            'abstract':'<jats:p>Evidence</jats:p>'}, 'SMJ')
        self.assertEqual(record['title'], 'Strategy & change')
        self.assertEqual(record['year'], 2024)
        self.assertEqual(record['abstract'], 'Evidence')
        self.assertEqual(record['authors'], 'A Smith')

    def test_filters_and_partial_failure(self):
        calls=[]
        def fetch(*args):
            calls.append(args)
            if args[0]=='asq': raise TimeoutError()
            return {'items':[normalize({'title':['Test'],'DOI':'10.1/a'},'SMJ')], 'total':25}
        result=search({'q':['strategy'],'journal':['asq','smj'],'from':['2020'],
                       'to':['2025'],'sort':['newest'],'page':['2']},fetch)
        self.assertEqual(len(result['items']),1)
        self.assertEqual(len(result['errors']),1)
        self.assertIn(('smj','strategy','2020','2025','newest',2), calls)

    def test_invalid_inputs(self):
        for params in ({'q':['']},{'q':['x'],'journal':['bad']},
                       {'q':['x'],'from':['2025'],'to':['2020']},
                       {'q':['x'],'page':['0']},{'q':['x'],'from':['abcd']}):
            with self.assertRaises(ValueError): search(params)

    def test_all_services_fail(self):
        def fail(*args): raise OSError()
        result=search({'q':['strategy']},fail)
        self.assertEqual(result['items'],[])
        self.assertEqual(len(result['errors']),4)

if __name__=='__main__': unittest.main()
