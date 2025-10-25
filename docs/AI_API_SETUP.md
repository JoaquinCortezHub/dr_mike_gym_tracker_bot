# AI API Setup Guide

This guide covers setting up the AI provider (OpenAI or Anthropic) for the Agno agent.

You can choose either **OpenAI** or **Anthropic** as your AI provider. Both work great!

---

## Option 1: OpenAI (Recommended for Cost)

OpenAI's GPT-4o-mini is fast, affordable, and works great for parsing workout messages.

### Step 1: Create OpenAI Account

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in to your account
3. You may need to add a payment method (credit card)

### Step 2: Get API Key

1. Click on your profile in the top-right corner
2. Select **"API keys"** or go directly to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Click **"+ Create new secret key"**
4. Give it a name: `Gym Tracker Bot`
5. Click **"Create secret key"**
6. **IMPORTANT:** Copy the key immediately - you won't be able to see it again!
   - It starts with `sk-` and looks like: `sk-proj-abc123...`

### Step 3: Configure Environment Variables

Add to your `.env` file:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Recommended Models

- **gpt-4o-mini** - Fast, cheap, great for this use case (Recommended)
- **gpt-4o** - More capable but more expensive
- **gpt-3.5-turbo** - Cheapest option but less reliable

### Pricing (as of 2025)

- **gpt-4o-mini:** ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- Typical cost per workout log: ~$0.0001 (essentially free for personal use)
- Expected monthly cost for daily use: **< $1**

---

## Option 2: Anthropic Claude (Recommended for Quality)

Claude is excellent at understanding natural language and context.

### Step 1: Create Anthropic Account

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Add credits to your account (minimum $5)

### Step 2: Get API Key

1. Go to **"API Keys"** in the left sidebar
2. Or visit [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
3. Click **"Create Key"**
4. Give it a name: `Gym Tracker Bot`
5. Click **"Create Key"**
6. **IMPORTANT:** Copy the key immediately!
   - It starts with `sk-ant-` and looks like: `sk-ant-api03-abc123...`

### Step 3: Configure Environment Variables

Add to your `.env` file:

```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

### Recommended Models

- **claude-3-5-sonnet-latest** - Best balance of quality and speed (Recommended)
- **claude-3-5-haiku-latest** - Fastest and cheapest
- **claude-3-opus-latest** - Most capable but slower and more expensive

### Pricing (as of 2025)

- **Claude 3.5 Sonnet:** ~$3 per 1M input tokens, ~$15 per 1M output tokens
- **Claude 3.5 Haiku:** ~$0.80 per 1M input tokens, ~$4 per 1M output tokens
- Typical cost per workout log: ~$0.001
- Expected monthly cost for daily use: **$1-3**

---

## Configuration Summary

Your `.env` file should have ONE of these configurations:

### For OpenAI:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### For Anthropic:
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

---

## Testing Your API Key

You can test if your API key works before running the bot:

### Test OpenAI
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

### Test Anthropic
```bash
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: YOUR_API_KEY_HERE" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{"model":"claude-3-5-sonnet-latest","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

---

## Troubleshooting

### "Invalid API key" error

**For OpenAI:**
- Make sure the key starts with `sk-proj-` or `sk-`
- Verify you copied the entire key
- Check if there are extra spaces in the `.env` file
- Ensure your OpenAI account has billing set up

**For Anthropic:**
- Make sure the key starts with `sk-ant-`
- Verify you copied the entire key
- Check if you have credits in your account
- Ensure the key hasn't been revoked

### "Rate limit exceeded" error

- You're making too many requests too quickly
- For OpenAI: Check your rate limits in the dashboard
- For Anthropic: Check your tier limits
- Consider adding delays between requests (already handled by the bot)

### "Insufficient credits/quota" error

**For OpenAI:**
- Add a payment method in your OpenAI dashboard
- Check if you have any remaining free credits

**For Anthropic:**
- Purchase credits in the Anthropic console
- Minimum purchase is usually $5

### Model not found error

- Verify the model name is correct
- Check the provider's documentation for current model names
- Some models may require special access

---

## Cost Management Tips

1. **Start with the cheapest model** (gpt-4o-mini or claude-haiku)
2. **Monitor usage** through your provider's dashboard
3. **Set billing alerts** to avoid surprises
4. **Use caching** (already implemented in the bot where possible)
5. For personal use, monthly costs should be minimal ($1-5)

---

## Security Best Practices

1. **Never share** your API keys
2. **Never commit** them to version control
3. **Rotate keys** periodically
4. **Set spending limits** in your provider dashboard
5. **Monitor usage** for unexpected spikes

---

## Switching Providers

You can easily switch between providers by changing the `.env` file:

```env
# Just change AI_PROVIDER and the corresponding API key
AI_PROVIDER=openai  # or 'anthropic'
```

Both providers work seamlessly with the Agno framework!

---

## Next Steps

Once your AI API is configured, you're ready to run the bot! See the main [README.md](../README.md) for usage instructions.
