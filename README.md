# promotions
Our squad is taking charge of the promotions functionality for an eCommerce web site backend which is a collection RESTful services for a client. 

The promotions resource is a representation of a special promotion or sale that is running
against a product or perhaps the entire store. Some examples are "buy 1 get 1 free", "20% off",
etc. Discount promotions usually apply for a given duration (e.g., sale for 1 week only). It's up to
you to get creative.

#### API calls
URL | Operation | Description
-- | -- | --
`GET /promotions` | READ | List all promotion
`GET /promotions/{promotion-id}` | READ | Fetch information for particular promotion
`POST /promotions` | CREATE | Create new promotion
`PUT /promotions/{promotion-id}` | UPDATE | Update particular promotion
`DELETE /promotions/{promotion-id}` | DELETE | Delete particular promotion
`GET /promotions/promotion-code={promotion-code}` | READ | Fetch promotions by promotion code
`POST /promotions/{promotion-id}/apply` | READ | Take a list of the product prices and check if the promotion can apply to them.
`GET /` |  | Display all available API routes


#### Run and Test
- Clone the repository using: `git@github.com:devops-fall-2019-promotions-squad/promotions.git`
- Start the Vagrant VM using : `vagrant up`
- After the VM has been provisioned ssh into it using: `vagrant ssh`
- cd into `/vagrant` using `cd /vagrant` and start the server using `FLASK_APP=service:app flask run -h 0.0.0.0`