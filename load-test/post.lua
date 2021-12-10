wrk.method = "POST"
wrk.body = '{"traits": [{ "trait_value": 123,"trait_key": "my_trait_key"},{"trait_value": true,"trait_key": "my_other_key"}],"identifier": "do_it_all_in_one_go_identity"}'
wrk.headers["Content-Type"] = "application/json"

