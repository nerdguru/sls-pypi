# Lambda Layers Explained

At re:Invent 2018, AWS introduced [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html), which
for Python functions enables required packages to be loaded separately from the main code and reused across multiple functions.

There's a great tutorial by [@gtangs that shows how to construct Lambda Layers both with and without the Serverless framework](
https://medium.com/@qtangs/creating-new-aws-lambda-layer-for-python-pandas-library-348b126e9f3e) that our layers here are derived from.

Our layers are pre-assembled and checked into the GitHub repo, but in case they need to be re-assembled, those instructions are supplied here.

On the file system, layers are laid out as follows prior to assembly:

```
core
  layers
    uigen
      get_layer_packages.sh
      requirements.txt
```
If you look at `get_layer_packages.sh`, it uses a local Docker instance to get a clean `pip install` of all the packages
listed in `requirements.txt`.  When executed, it will form an additional folder structure under `uigen/python` that will be referenced
in `serverless.yml`.

To assemble the uigen layer, execute the following from the `core` folder:

```
pushd layers/uigen && chmod +x get_layer_packages.sh && ./get_layer_packages.sh && popd
```

With the layer now assembled, it can be referenced in `serverless.yml`.  
Look under the `provider:` section for the `layer:` section for details.

Once `serverless.yml` is aware of the layer, it can be referenced in individual function definitions.
For example, the `webProcess` function references the `UIgen` layer but note the peculiar naming syntax.
In order for the reference to work correctly, the name of the layer has to have the suffix `LambdaLayer`
appended to it.
