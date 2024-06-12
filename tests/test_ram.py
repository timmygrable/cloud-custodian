from .common import BaseTest
import time


class TestRAM(BaseTest):

    def test_ram_query(self):
        session_factory = self.replay_flight_data("test_ram_query")
        p = self.load_policy(
            {"name": "list-ram", "resource": "ram"},
            session_factory=session_factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_ram_delete(self):
        session_factory = self.replay_flight_data("test_ram_delete")
        p = self.load_policy(
            {
                "name": "delete-ram",
                "resource": "ram",
                "filters": [
                    {
                        "type": "value",
                        "key": "name",
                        "value": "test2",
                        "op": "eq"
                    }
                ],
                "actions": [
                    {
                        "type": "delete",
                    }
                ]
            },
            session_factory=session_factory,
        )
        resources = p.run()

        time.sleep(3)
        resources = session_factory().client("ram").get_resource_shares(
            resourceOwner="SELF",
            resourceShareArns=
            ["arn:aws:ram:us-east-1:644160558196:resource-share/5547ad79-7574-4fff-8514-72b1ae700963"]
        )

        self.assertEqual(resources["resourceShares"][0]["status"], "DELETED")
