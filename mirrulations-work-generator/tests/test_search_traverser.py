from mirrgen.search_iterator import SearchIterator
from mirrcore.regulations_api import RegulationsAPI
from mirrmock.mock_dataset import MockDataSet


def test_iterate_one_page(requests_mock, mocker):
    mocker.patch('time.sleep')

    results = MockDataSet(150).get_results()

    requests_mock.get('https://api.regulations.gov/v4/documents', results)
    api = RegulationsAPI('FAKE_KEY')
    count = 0
    for _ in SearchIterator(api, 'documents', '2021-06-08 00:00:00'):
        count += 1

    assert count == 1


def test_iterate_four_pages(requests_mock, mocker):

    mocker.patch('time.sleep')

    results = MockDataSet(850).get_results()

    requests_mock.get('https://api.regulations.gov/v4/documents', results)
    api = RegulationsAPI('FAKE_KEY')
    count = 0
    for _ in SearchIterator(api, 'documents', '2021-06-08 00:00:00'):
        count += 1

    assert count == 4


def test_iterate_5650_results(requests_mock, mocker):

    mocker.patch('time.sleep')

    results = MockDataSet(5650).get_results()
    requests_mock.get('https://api.regulations.gov/v4/documents', results)
    api = RegulationsAPI('FAKE_KEY')

    count = 0
    for _ in SearchIterator(api, 'documents', '2021-06-08 00:00:00'):
        count += 1

    assert count == 23


def test_date_converted_utc_to_est(requests_mock, mocker):
    mocker.patch('time.sleep')

    results = MockDataSet(5500, start_date='2020-01-01 05:00:00').get_results()
    requests_mock.get('https://api.regulations.gov/v4/documents', results)
    api = RegulationsAPI('FAKE_KEY')

    for _ in SearchIterator(api, 'documents', '2020-01-01 05:00:00'):
        pass

    # The first 20 pages will have the date in EST (-5 because no DST in Dec)
    for index in range(20):
        call = requests_mock.request_history[index]
        # [0] because the query string is apparently a list
        # Also note that lastModifiedDate is make lower-case by request(-mock)
        assert call.qs['filter[lastmodifieddate][ge]'][0] == \
               '2020-01-01 00:00:00'

    # The last 2 pages will have 5000 seconds added because the MockDataSet
    # adds one second to each date.  5000 seconds = 83 minutes and 20 seconds
    for index in range(21, 23):
        call = requests_mock.request_history[index]
        assert call.qs['filter[lastmodifieddate][ge]'][0] == \
               '2020-01-01 01:23:20'


def test_fix_url():
    api = RegulationsAPI('FAKE_KEY')
    url = 'https://api.regulations.gov/v4/comments'\
        '?sort=lastModifiedDate&page%5Bsize%5D=250'\
        '&filter%5BlastModifiedDate%5D%5Bge%5D=2023-03-17+16%3A00%3A04'\
        '&page%5Bnumber%5D=7&api_key=TEST_KEY'
    expected_url = 'https://api.regulations.gov/v4/comments'\
        '?sort=lastModifiedDate&page[size]=250&filter'\
        '[lastModifiedDate][ge]=2023-03-17+16:00:04&page[number]=7'
    iterator = SearchIterator(api, 'comments', '2023-03-17 16:00:04')
    assert expected_url == iterator.fix_url(url)
