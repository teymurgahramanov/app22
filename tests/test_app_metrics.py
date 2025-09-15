from fastapi import status


class TestAppMetrics:
    def test_metrics_exposed(self, test_client):
        resp = test_client.get('/metrics')
        assert resp.status_code == status.HTTP_200_OK
        # content-type should be text/plain for Prometheus
        assert 'text/plain' in resp.headers.get('content-type', '')

    def test_counter_increment(self, test_client):
        # increment a counter
        r = test_client.post('/metrics/counter?name=reqs&inc=3')
        assert r.status_code == status.HTTP_200_OK
        # metrics should contain the counter with value >= 3
        m = test_client.get('/metrics').text
        assert 'app_counter_total{name="reqs"} 3.0' in m or 'app_counter_total{name="reqs"} 3' in m

    def test_gauge_set_inc_dec(self, test_client):
        # set gauge, then inc, then dec
        assert test_client.post('/metrics/gauge?name=load&set_value=5').status_code == 200
        assert test_client.post('/metrics/gauge?name=load&inc=2').status_code == 200
        assert test_client.post('/metrics/gauge?name=load&dec=1').status_code == 200
        m = test_client.get('/metrics').text
        # final should be 6
        assert 'app_gauge{"name"="load"} 6.0' in m or 'app_gauge{"name"="load"} 6' in m or 'app_gauge{name="load"} 6.0' in m or 'app_gauge{name="load"} 6' in m

    def test_histogram_observe(self, test_client):
        assert test_client.post('/metrics/histogram?name=latency&observe=0.5').status_code == 200
        assert test_client.post('/metrics/histogram?name=latency&observe=1.5').status_code == 200
        m = test_client.get('/metrics').text
        # histogram should have sum and count
        assert 'app_histogram_sum{name="latency"}' in m
        assert 'app_histogram_count{name="latency"}' in m


