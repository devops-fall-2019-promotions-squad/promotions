[![Build Status](https://travis-ci.org/devops-fall-2019-promotions-squad/promotions.svg?branch=master)](https://travis-ci.org/devops-fall-2019-promotions-squad/promotions)

# promotions
Our squad is taking charge of the promotions functionality for an eCommerce web site backend which is a collection RESTful services for a client. 

The promotions resource is a representation of a special promotion or sale that is running
against a product or perhaps the entire store. Some examples are "20% off",
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
`POST /promotions/{promotion-id}/apply` | READ | Take a list of the products(each product should at least has product ID and price) and check if the promotion can apply to them.
`GET /` | READ | Display all available API routes


## Prerequisite Installation using Vagrant VM

The easiest way to use this lab is with **Vagrant** and **VirtualBox**. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

```bash
    git clone https://github.com/devops-fall-2019-promotions-squad/promotions.git
    cd promotions
    vagrant up
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
```

## Manually running the Tests

Run the tests using `nose`

```bash
    cd /vagrant/
    nosetests
```

**Nose** is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red. It also has `--with-coverage` specified so that code coverage is included in the tests.

The Code Coverage tool runs with `nosetests` so to see how well your test cases exercise your code just run the report:

```bash
    coverage report -m
```

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases.

To run the service use `flask run` (Press Ctrl+C to exit):

```bash
    FLASK_APP=service:app flask run -h 0.0.0.0
```

You must pass the parameters `-h 0.0.0.0` to have it listed on all network adapters to that the post can be forwarded by `vagrant` to your host computer so that you can open the web page in a local browser at: http://localhost:5000

When you are done, you can exit and shut down the vm with:

```bash
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
    vagrant destroy
```
