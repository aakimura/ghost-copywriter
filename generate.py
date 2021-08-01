import openai


def generate(model, prompt, temperature=0.5, top_p=1,frequency_penalty=0,
             presence_penalty=0, stop='.\n\n'):
    """
    Generate a completion with a new prompt using a pre-trained model

    Parameters
    ----------
    model: [string] ID of your pre-trained model.
    prompt: [string] Text block containing your prompt. Remember to use the
            same parameters as the ones you used to train your model.
            Finish your prompt with `\n\n###\n\n`.and
    tempereature: [float] Control how creative the model should be. 1 = most
                  creative, 0 = more 'robotic' or strict.

    Returns
    -------
    JSON with the completion's parameters.
    """
    completion = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        max_tokens=60)

    return completion