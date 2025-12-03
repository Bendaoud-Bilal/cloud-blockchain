# 🚀 Blockchain Deployment Guide for Render.com

## Complete Step-by-Step Guide (Beginner Friendly)

This guide will walk you through deploying your blockchain network to Render.com with 3 nodes + 1 client, all communicating over HTTPS with Redis persistence.

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Understanding the Architecture](#-understanding-the-architecture)
3. [Preparing Your Code](#-preparing-your-code)
4. [Creating a Render Account](#-creating-a-render-account)
5. [Deploying with Blueprint (Recommended)](#-method-1-deploy-with-blueprint-recommended)
6. [Manual Deployment](#-method-2-manual-deployment)
7. [Configuring Peer Nodes](#-configuring-peer-nodes)
8. [Testing Your Deployment](#-testing-your-deployment)
9. [Troubleshooting](#-troubleshooting)
10. [Managing Your Deployment](#-managing-your-deployment)

---

## 📝 Prerequisites

Before you start, make sure you have:

1. **A GitHub account** - [Sign up here](https://github.com/signup)
2. **Git installed** on your computer - [Download here](https://git-scm.com/downloads)
3. **Your blockchain code** pushed to a GitHub repository
4. **A Render account** (we'll create this in the guide)

---

## 🏗 Understanding the Architecture

Your deployed blockchain will have:

```
┌─────────────────────────────────────────────────────────────────┐
│                          RENDER.COM                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐│
│  │  blockchain-node1│  │  blockchain-node2│  │  blockchain-node3││
│  │  (Web Service)   │  │  (Web Service)   │  │  (Web Service)   ││
│  │                  │◄─┼──────────────────►│◄─┤                  ││
│  │  https://...     │  │  https://...     │  │  https://...     ││
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘│
│           │                     │                     │          │
│           └─────────────────────┼─────────────────────┘          │
│                                 │                                │
│                    ┌────────────▼────────────┐                   │
│                    │   blockchain-redis     │                   │
│                    │   (Key Value Store)    │                   │
│                    │   Stores chain data    │                   │
│                    └─────────────────────────┘                   │
│                                                                  │
│  ┌──────────────────┐                                            │
│  │ blockchain-client│ ◄── Wallet (Create keys, send transactions)│
│  │  (Web Service)   │                                            │
│  │  https://...     │                                            │
│  └──────────────────┘                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What Each Service Does:

| Service           | Purpose                                    | URL Example                            |
| ----------------- | ------------------------------------------ | -------------------------------------- |
| blockchain-node1  | Blockchain node 1 (mining, chain storage)  | https://blockchain-node1.onrender.com  |
| blockchain-node2  | Blockchain node 2 (mining, chain storage)  | https://blockchain-node2.onrender.com  |
| blockchain-node3  | Blockchain node 3 (mining, chain storage)  | https://blockchain-node3.onrender.com  |
| blockchain-client | Wallet (create keys, make transactions)    | https://blockchain-client.onrender.com |
| blockchain-redis  | Key Value store (persists blockchain data) | Internal connection only               |

---

## 📦 Preparing Your Code

### 1. Make Sure Your Code is Ready

Your repository should have these files:

```
blockchain-python-tutorial/
├── blockchain/
│   ├── blockchain.py          # ✅ Updated for Render
│   └── templates/
│       ├── index.html
│       └── configure.html     # ✅ Updated for Render
├── blockchain_client/
│   ├── blockchain_client.py   # ✅ Updated for Render
│   └── templates/
│       ├── index.html
│       ├── make_transaction.html  # ✅ Updated for Render
│       └── view_transactions.html # ✅ Updated for Render
├── requirements.txt           # ✅ With gunicorn and redis
├── render.yaml                # ✅ Blueprint file
├── runtime.txt                # ✅ Python version
├── gunicorn.conf.py           # ✅ Gunicorn config
└── reset_blockchain.py        # ✅ Reset script
```

### 2. Push Your Code to GitHub

If you haven't already, push your bc-cloud branch to GitHub:

```bash
# Navigate to your project folder
cd blockchain-python-tutorial

# Make sure you're on bc-cloud branch
git checkout bc-cloud

# Add all new files
git add .

# Commit the changes
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin bc-cloud
```

---

## 🎯 Creating a Render Account

### Step 1: Go to Render.com

1. Open your browser and go to [https://render.com](https://render.com)
2. Click **"Get Started for Free"** (top right)

### Step 2: Sign Up with GitHub

1. Click **"GitHub"** button to sign up with your GitHub account
2. Click **"Authorize Render"** to allow Render to access your repositories
3. Complete the account setup (email verification if needed)

### Step 3: Explore the Dashboard

After signing up, you'll see the Render Dashboard:

- **Services** - Where your web apps will appear
- **Databases** - Where Redis will appear
- **Blueprints** - For deploying from render.yaml

---

## 🚀 Method 1: Deploy with Blueprint (Recommended)

The Blueprint method deploys all 5 services automatically from your `render.yaml` file.

### Step 1: Create a New Blueprint

1. In the Render Dashboard, click **"Blueprints"** in the left sidebar
2. Click **"New Blueprint Instance"**

### Step 2: Connect Your Repository

1. If you haven't connected your GitHub, click **"Connect account"**
2. Select **"Configure"** to choose which repositories Render can access
3. Select your **blockchain-python-tutorial** repository
4. Click **"Save"**

### Step 3: Select the Repository

1. Find and click on **blockchain-python-tutorial**
2. Select the **bc-cloud** branch
3. Click **"Apply"**

### Step 4: Review and Deploy

1. Render will detect your `render.yaml` file
2. Review the services to be created:
   - blockchain-node1 (Web Service)
   - blockchain-node2 (Web Service)
   - blockchain-node3 (Web Service)
   - blockchain-client (Web Service)
   - blockchain-redis (Key Value)
3. Click **"Apply"** to start deployment

### Step 5: Wait for Deployment

- This will take **5-10 minutes** for all services
- Watch the build logs for each service
- Green checkmarks ✅ mean success
- Red X ❌ means there was an error (check logs)

### Step 6: Get Your Service URLs

After deployment, go to the **Dashboard** and note down each service URL:

| Service           | Your URL                                      |
| ----------------- | --------------------------------------------- |
| blockchain-node1  | `https://blockchain-node1-XXXX.onrender.com`  |
| blockchain-node2  | `https://blockchain-node2-XXXX.onrender.com`  |
| blockchain-node3  | `https://blockchain-node3-XXXX.onrender.com`  |
| blockchain-client | `https://blockchain-client-XXXX.onrender.com` |

> **📝 Note:** The `XXXX` will be random characters added by Render.

---

## 🔧 Method 2: Manual Deployment

If the Blueprint method doesn't work, deploy each service manually.

### Step 1: Create Key Value Store (Redis)

1. In Dashboard, click **"New +"** → **"Key Value"** (formerly Redis)
2. Configure:
   - **Name:** `blockchain-redis`
   - **Region:** Frankfurt (or closest to you)
   - **Plan:** Free
3. Click **"Create Key Value"**
4. Copy the **Internal Connection String** (you'll need this)

### Step 2: Create Node 1

1. Click **"New +"** → **"Web Service"**
2. Connect your repository if not already connected
3. Select **blockchain-python-tutorial**
4. Configure:

| Setting        | Value                                                                    |
| -------------- | ------------------------------------------------------------------------ |
| Name           | `blockchain-node1`                                                       |
| Region         | Frankfurt                                                                |
| Branch         | `bc-cloud`                                                               |
| Root Directory | `blockchain`                                                             |
| Runtime        | Python 3                                                                 |
| Build Command  | `pip install -r ../requirements.txt`                                     |
| Start Command  | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 blockchain:app` |

5. Add Environment Variables (click "Advanced"):

| Key          | Value                      |
| ------------ | -------------------------- |
| `FLASK_HOST` | `0.0.0.0`                  |
| `NODE_ID`    | `node1`                    |
| `REDIS_URL`  | (paste Internal Redis URL) |

6. Click **"Create Web Service"**

### Step 3: Create Node 2 & 3

Repeat Step 2 for:

- **blockchain-node2** (with `NODE_ID` = `node2`)
- **blockchain-node3** (with `NODE_ID` = `node3`)

### Step 4: Create Client

1. Click **"New +"** → **"Web Service"**
2. Configure:

| Setting        | Value                                                                           |
| -------------- | ------------------------------------------------------------------------------- |
| Name           | `blockchain-client`                                                             |
| Region         | Frankfurt                                                                       |
| Branch         | `bc-cloud`                                                                      |
| Root Directory | `blockchain_client`                                                             |
| Runtime        | Python 3                                                                        |
| Build Command  | `pip install -r ../requirements.txt`                                            |
| Start Command  | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 blockchain_client:app` |

3. Add Environment Variable:

   - `FLASK_HOST` = `0.0.0.0`

4. Click **"Create Web Service"**

---

## 🔗 Configuring Peer Nodes

After all services are deployed, you need to configure each node to know about its peers.

### Step 1: Get All Node URLs

Go to Dashboard and copy each node's URL:

- Node 1: `https://blockchain-node1-xxxx.onrender.com`
- Node 2: `https://blockchain-node2-xxxx.onrender.com`
- Node 3: `https://blockchain-node3-xxxx.onrender.com`

### Step 2: Configure Node 1 Environment Variables

1. Click on **blockchain-node1** in Dashboard
2. Go to **"Environment"** tab
3. Add/Update these variables:

| Key          | Value                                                                                   |
| ------------ | --------------------------------------------------------------------------------------- |
| `OWN_URL`    | `https://blockchain-node1-xxxx.onrender.com`                                            |
| `PEER_NODES` | `https://blockchain-node2-xxxx.onrender.com,https://blockchain-node3-xxxx.onrender.com` |

4. Click **"Save Changes"**
5. The service will automatically redeploy

### Step 3: Configure Node 2 Environment Variables

| Key          | Value                                                                                   |
| ------------ | --------------------------------------------------------------------------------------- |
| `OWN_URL`    | `https://blockchain-node2-xxxx.onrender.com`                                            |
| `PEER_NODES` | `https://blockchain-node1-xxxx.onrender.com,https://blockchain-node3-xxxx.onrender.com` |

### Step 4: Configure Node 3 Environment Variables

| Key          | Value                                                                                   |
| ------------ | --------------------------------------------------------------------------------------- |
| `OWN_URL`    | `https://blockchain-node3-xxxx.onrender.com`                                            |
| `PEER_NODES` | `https://blockchain-node1-xxxx.onrender.com,https://blockchain-node2-xxxx.onrender.com` |

### Step 5: Wait for Redeployment

After updating environment variables, each service will redeploy automatically.
Wait for all services to show **"Live"** status.

---

## 🧪 Testing Your Deployment

### 1. Check Health Endpoints

Open each URL in your browser and add `/health`:

```
https://blockchain-node1-xxxx.onrender.com/health
```

You should see:

```json
{
  "status": "healthy",
  "node_id": "abc123...",
  "chain_length": 1,
  "pending_transactions": 0,
  "registered_nodes": 2
}
```

### 2. Test Node Registration

After ~30 seconds, check if nodes found each other:

```
https://blockchain-node1-xxxx.onrender.com/nodes/get
```

Should show:

```json
{
  "nodes": [
    "https://blockchain-node2-xxxx.onrender.com",
    "https://blockchain-node3-xxxx.onrender.com"
  ]
}
```

### 3. Test Mining

Go to any node's web interface:

```
https://blockchain-node1-xxxx.onrender.com
```

Click **"Mine"** button. After mining, check chain on all nodes:

```
https://blockchain-node1-xxxx.onrender.com/chain
https://blockchain-node2-xxxx.onrender.com/chain
https://blockchain-node3-xxxx.onrender.com/chain
```

All should show the same chain length!

### 4. Test Transactions

1. Open the wallet client:

   ```
   https://blockchain-client-xxxx.onrender.com
   ```

2. Generate a new wallet (copy the keys!)

3. Make a transaction:

   - Enter your public key as sender
   - Enter any recipient address
   - Enter an amount
   - Click "Generate Transaction"
   - In the **Node URL** field, enter: `https://blockchain-node1-xxxx.onrender.com`
   - Click "Send Transaction"

4. Mine on any node to confirm the transaction

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Service shows "Deploy failed"

**Check build logs:**

1. Click on the service
2. Click "Events" tab
3. Click on the failed deploy
4. Read the logs

**Common causes:**

- Wrong Root Directory
- Missing requirements.txt
- Syntax error in Python code

#### 2. "Redis not available" in logs

**Solution:**

1. Check if blockchain-redis is running
2. Verify REDIS_URL is correct in environment variables
3. Redeploy the service

#### 3. Nodes not finding each other

**Solution:**

1. Check PEER_NODES environment variable
2. Make sure URLs are complete (with https://)
3. Separate URLs with comma, no spaces
4. Wait 30 seconds and refresh

#### 4. "Connection refused" errors

**Cause:** Service is sleeping (free tier limitation)

**Solution:**

- Access the service URL to wake it up
- Wait 30 seconds for it to start
- Consider upgrading to paid tier for always-on

#### 5. Mining is slow

**Cause:** Free tier has limited CPU

**Solution:**

- This is normal for free tier
- Mining will take 10-30 seconds
- Consider reducing MINING_DIFFICULTY for testing

### Checking Logs

To view logs for debugging:

1. Click on the service
2. Click **"Logs"** tab
3. Look for error messages

---

## 🛠 Managing Your Deployment

### Updating Your Code

When you push new code to GitHub:

```bash
git add .
git commit -m "Your update message"
git push origin bc-cloud
```

Render will automatically redeploy all services.

### Restarting a Service

1. Go to the service in Dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### Resetting the Blockchain

Use the reset script:

```bash
python reset_blockchain.py --nodes https://blockchain-node1-xxxx.onrender.com --secret YOUR_RESET_SECRET
```

Get the RESET_SECRET from the service's environment variables.

### Monitoring Usage

Check your usage:

1. Go to Dashboard
2. Click **"Usage"** in sidebar
3. Monitor free tier limits

### Free Tier Limitations

| Resource     | Free Tier Limit         |
| ------------ | ----------------------- |
| Web Services | 750 hours/month         |
| Key Value    | 25 MB                   |
| Auto-sleep   | After 15 min inactivity |
| Bandwidth    | 100 GB/month            |

---

## 📚 Quick Reference

### Important URLs

| Service | Path                | Purpose                   |
| ------- | ------------------- | ------------------------- |
| Node    | `/`                 | Web interface             |
| Node    | `/health`           | Health check              |
| Node    | `/chain`            | View blockchain           |
| Node    | `/mine`             | Mine a block              |
| Node    | `/nodes/get`        | List peers                |
| Node    | `/nodes/register`   | Register peers            |
| Node    | `/nodes/resolve`    | Sync chain                |
| Node    | `/transactions/get` | View pending transactions |
| Client  | `/`                 | Wallet interface          |
| Client  | `/wallet/new`       | Generate new wallet       |
| Client  | `/make/transaction` | Create transaction        |

### Environment Variables

| Variable       | Service | Purpose                   |
| -------------- | ------- | ------------------------- |
| `PORT`         | All     | Port (set by Render)      |
| `FLASK_HOST`   | All     | Host binding (0.0.0.0)    |
| `NODE_ID`      | Nodes   | Unique node identifier    |
| `OWN_URL`      | Nodes   | This node's public URL    |
| `PEER_NODES`   | Nodes   | Comma-separated peer URLs |
| `REDIS_URL`    | Nodes   | Redis connection string   |
| `RESET_SECRET` | Nodes   | Secret for reset endpoint |

---

## 🎉 Congratulations!

You've successfully deployed a distributed blockchain network to the cloud!

Your nodes are now:

- ✅ Communicating over HTTPS
- ✅ Persisting data to Redis
- ✅ Auto-registering with peers
- ✅ Syncing chains on new blocks
- ✅ Broadcasting transactions

### Next Steps

1. **Share your client URL** with friends to test transactions
2. **Monitor the logs** to understand how nodes communicate
3. **Experiment** with mining from different nodes
4. **Try the reset script** to start fresh

### Need Help?

- Check Render documentation: https://render.com/docs
- View service logs for errors
- Check the health endpoint first

Happy Blockchaining! 🔗⛓️
