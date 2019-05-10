# Serverless PyPi With Metrics
`pip` is amazing and lets Python coders bounce off each other by sharing code
easily.  The back end of pip is provided by [PyPi.org](http://pypi.org) and while that eases the burden of finding useful packages, it doesn't quite forster the same community dynamics through statistics as other languages do.

For example, take a look at the statistics available for the [requests package on pip](https://pypi.org/project/requests/) and compare that to its [equivalent package on npm](https://www.npmjs.com/package/request).  The latter reports things like daily downloads, dependencies in both directions, and a wide variety of GitHub metrics that make the experience of using it richer because it is easier for members of the community to judge the state of the package through the behavior of others.  

So if you were trying to build a Python-based sub-community, it would be nice to have the functionality of a `pip install` but have back end metrics closer to what `npm` provides.  And if you were going to build such a thing in 2019, you'd do it with a serverless application architecture.  That's what this project is.

If you'd like to understand how it all works, check out the [architecture documentation](docs/architecture.md).

If you'd just like to get it up and running, check out the [quickstart](docs/quickstart.md)

## Acknowledgements
Like any modern project, this one stands on the shoulders of others that are leveraged heavily in different ways here:

* [s3pypi](https://github.com/novemberfiveco/s3pypi) - Provides a really nice set of CloudFormation templates for setting up an S3 bucket with a combination of CloudFront and AWS Certificate Manager so that `pip install` will work correctly.
* [Serverless Framework](http://serverless.com) - The leaders in serverless tooling eases the packaging and trigger management for functions.
* [Serverless Stack](https://serverless-stack.com/) - The canonical real world example for building secure, serverless webapps.
* [github-cognito-openid-wrapper](https://github.com/TimothyJones/github-cognito-openid-wrapper) - Bridges the gap between Cognito and the GitHub login system so that API endpoints can be secured using an authenticator familiar to developers.
