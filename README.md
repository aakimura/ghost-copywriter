# Ghost Copywriter

Ghost Copywriter is an AI assistant for product managers to launch a landing page in seconds. It only takes the product description and all the copy is written by the assistant.

It can be paired up with a landing page builder that puts every piece into place. Speeding up the process of launching early prototypes.

## How it works?

It uses a fine-tuned model in GPT-3 using the best examples of copy for websites.

## Using OpenAI

GPT-3 was used to create the model. However, some limitations exist regarding the input (prompt) and output (completion). For instance, GPT-3 requests that only one completion should be done per prompt. That is, there should be a "chained" process in which the first input will human made, and the subsequent will be automatic calls to the API.

Another limitation is the usage of JSON Lines files. This is an extension to the regular JSON format in which each row represents an instance. This  format is not always supported by editors.

### Human-friendly editing

As described above, JSON Lines files is required by GPT-3 to train the model. However, this format is very unfriendly for human reading. For example:
```JSON
{"prompt":"Company: Gousto\nFeatures: 50+ recipes a week, cooked from 10 mins. Family classics, global cuisines plus Joe Wicks's health range. Tasty plant based and gluten free options. Fresh ingredients from trusted suppliers. 100% British meat. All recipes tried, tested and loved by our chefs and customers. Easy-to-follow recipe cards. Precise ingredients with zero food waste. Free, contactless delivery, any day you like.\n\n###\n\n", "completion":"Product: Recipe kit boxes which include ready-measured, fresh ingredients and easily followed recipes.\nHeadline: Endless choice in a recipe box\nSupporting copy: Over 50 recipes every week.\nCall to action: Get started\n"}
```

Thus, a helper was written in `dehumanize.py` to accept CSV formats which are much human-friendly than editing JSON Lines files directly.

## References

- [OpenAI documentation](https://beta.openai.com/docs/guides/fine-tuning) on fine-tuned models.
- [Sleeknote article](https://sleeknote.com/blog/copywriting-examples) on excellent website copy.
- [Hubspot article](https://blog.hubspot.com/marketing/copywriting-examples) on copywriting examples.
- [Unbounce artile](https://unbounce.com/landing-page-articles/the-anatomy-of-a-landing-page/) on the anatomy of a landing page.
