
Amir, by the end of this pod, what are
0:02
we going to learn?
0:03
I'm going to first talk through what
0:05
OpenAI came out of yesterday with the
0:07
agent builder, the chat kit, the
0:08
widgets, and we're going to build a demo
0:11
chatbot using the chat kit SDK on a
0:15
website and we're going to essentially
0:16
have it pull data from our vector store,
0:19
our multi- aent workflows, and have it
0:21
answer questions. The chatbot is going
0:23
to let you know whether you're actually
0:24
a customer or a lead and then get the
0:26
information from you to pass it on to
0:28
your sales team or answer a support
0:29
ticket.
0:29
So air, are people going to understand
0:32
how to use agent builder by the end of
0:34
this?
0:35
That's exactly what we're going to
0:36
cover. I'm going to try my best to show
0:38
them what it takes to actually build
0:39
your own agent workflow using the new
0:41
agent builder, how it's different from
0:44
the other kind of tools out there, and
0:46
how you can get started as well.
0:48
Okay, let's start.
0:51
mind.
0:55
[Music]
Overview of Agent Builder
0:57
Cool. All right, let's jump into it. So,
0:59
the key three things that came out of
1:01
the dev day yesterday was agent builder,
1:04
chat kit, and widgets. And I'm going to
1:05
talk through what each individual one
1:07
actually is and what it means. So
1:10
typically, you know, anytime we've been
1:11
wanting to build multi- aent workflows,
1:14
we've had to use custom code to actually
1:16
kind of create a parallel sequence or a
1:19
multi- aent orchestration using code and
1:21
say, okay, assistant one talk to
1:23
assistant two and then pass through data
1:25
or a set of instructions. What OpenAI
1:28
has done with their new update is
1:30
they've created a visual interface for
1:31
you to actually build workflows using
1:34
agents and actually create parallel
1:37
agents if you wanted to or sequential
1:39
like steps in an agent workflow and have
1:41
it call tools do web search or file all
1:44
visually instead of using code. So it's
1:46
really interesting because you can
1:47
essentially now hold data as context
1:50
from a vector store. So it's like a
1:51
storage file and then also evaluate the
1:54
responses, refine it and then create
1:56
even guard rails for um safety and
1:58
quality of the agent responses. The key
2:01
takeaway here is that it's essentially
2:02
reducing the barrier for um
2:05
non-technical people to get started with
2:06
building multi- aent workflows. And what
2:09
this all means and how it ties in
2:10
together is essentially goes into
2:12
chatkit and widgets. So what chatkit is
Overview of ChatKit
2:14
is now um a new capability um where it's
2:18
essentially an SDK and you can connect
2:22
your um agent builder workflow into
2:26
chatkit and then serve it on a front
2:27
end. So in simple terms you know anytime
2:30
you've seen a chatbot on a website um
2:33
that's typically connected to a third
2:35
party service that is pulling data and
2:37
you've kind of created these responses.
2:39
In this demo today, we're going to
2:40
recreate our own that's trained our own
2:42
data and has a set of instructions and
2:44
we're going to use chat for it. So, what
2:46
we're going to do is we're going to
2:47
build a workflow in uh the agent builder
2:51
and then we're going to take that
2:52
workflow ID or that kind of template,
2:54
put it into chat UI, set up a server,
2:57
add it to our website and then
2:59
essentially have customers interact with
3:00
that chatbot to give their information
3:02
to learn more about a product or answer
3:04
a specific support ticket. The last
Overview of Widgets
3:06
thing is the widgets. Widgets are
3:08
essentially a new set of dynamic
3:10
components that you can add into chat
3:12
interfaces and conversations that can
3:15
display data. So, say for example, if
3:17
you have um
3:19
your agent connected to a Shopify store
3:21
and you're pulling uh through the MCP,
3:23
you're pulling Shopify information, you
3:25
can create a custom component that
3:26
displays it to the user that says, "Oh,
3:28
here's like what you ordered. Um here's
3:30
the, you know, estimated delivery time
3:32
and here's how it was sold." And you
3:34
know, you get your details. It's like a
3:35
dynamic UI essentially as part of the
3:37
chat interface.
3:38
God bless you, Amir.
3:40
Yeah.
3:41
All right, great. Let's jump into it.
3:43
Okay, so we covered all three big major
3:46
updates. Obviously, Sora 2 and the API,
3:48
uh, GBT5 Pro and the API, but I think
3:50
what's really interesting is just the
3:52
door and opportunities this opens up for
3:54
a lot of people that want to start
3:55
building multi-agent workflows. So the
Building a workflow with classifier and support/lead agents
3:57
first thing that we're going to get into
3:59
is uh jumping into actually the OpenAI
4:02
agent builder. And how it works is you
4:05
have a set of nodes that you can
4:06
connect. So each node is representative
4:09
of a specific set of actions. So you can
4:11
collect um you can add tools. So for
4:14
example, if you want to pull relevant
4:15
information or you want to add guard
4:17
rails and I'll show what that looks like
4:19
and what that means or MCPS. And you can
4:21
also add logic. So you can determine how
4:24
you want the agent to proceed based on
4:26
logic and conditions that you set. And
4:28
then you can also transform data as
4:30
well. In this specific demo, what we
4:33
want to do is we build want to build a
4:34
build build a workflow that achieves two
4:37
things. It receives a customer. It
4:41
receives a user input and it determines
4:43
whether or not this user is an existing
4:46
customer or a new lead. It classifies it
4:50
and then based on that logic passes on
4:52
to two separate agents. Agent number one
4:55
is if it's a c existing customer answer
4:58
the support ticket using existing
5:00
knowledgebased data. So I've actually
5:02
scraped our entire knowledge base and um
5:05
data pertaining to our product and gave
5:07
it as a vector store. So it's
5:08
referencing that as context or agent
5:10
number two. If the agent is uh
5:13
determines and classifies this as a
5:15
lead, it then um uh asks for information
5:20
about the customer to then you know as a
5:22
next step pass it on to our um you know
5:24
to our database or message us on Slack
5:27
for example if we have a Slack MCP. It
5:29
meant it's meant to capture that data
5:31
and then play back to the customer and
5:32
say hey we'll follow up for a demo and
5:33
let's book you for a demo. So what we've
5:36
done here is essentially um we have a
5:39
start input here which is input as text
5:41
which is a message that you get. Next is
5:44
the classifier. This classifier agent
5:46
essentially we've we've named it and we
5:48
gave it a prompt and we basically say
5:50
hey you know we want you to look at the
5:52
inquiry and tell us if this is an
5:54
existing customer with a support ticket
5:56
or a new lead and we want you to analyze
5:59
the message and determine whether or not
6:01
how you get to that conclusion. And we
6:02
gave some examples as well. So like
6:04
here's an example of what a new lead
6:05
would look like or here's an example of
6:07
someone that is um an existing customer.
6:11
Once once it's done that, we have a
6:14
logic in place that says uh classify
6:16
that inquiry as an existing customer
6:18
with the support question or a new user
6:21
based on that data. And essentially um
6:24
if once it's once it's been classified
6:27
from here, if it's an existing customer,
6:29
because the response here is essentially
6:31
um like we're saying the response is new
6:34
customer. Oh, I got my cat in front of
6:36
me right here. If um if if it's um if
6:40
it's a new customer uh pass it on to the
6:44
lead agent if it's an existing customer
6:46
customer uh pass it on to support agent
6:48
and how it works is essentially u based
6:50
on this logic here we say if the input
6:53
is an existing customer
6:55
pass it on to the customer support agent
6:59
and this customer support agent
7:00
essentially it's trained on our data and
7:03
it has a set of rules that it follows
7:05
and helps them troubleshoot any
7:06
questions they they have.
7:08
Okay. How did you how did you come up
7:10
with those instructions?
7:11
Um, so you can actually write the
7:13
instructions yourself, but what's really
7:15
cool is you can actually either use chat
7:17
GBT to say, um, I want you to act as a
7:20
prompt generator or a helpful assistant
7:22
that can help me generate prompts. I
7:24
want to achieve X. Tell me how we can
7:26
get there. So I usually most of the time
7:28
use chat GBT or just from creating so
7:31
many prompts, I know how to get there.
7:32
Um, you can use it to give a prompt back
7:36
to you. You're essentially it's very
7:37
meta. You're using an agent to create
7:38
agents agent prompts. And um what you
7:42
can also do as well is if you ever write
7:44
a simple prompt. So say for example um
7:47
you want to enhance this. So you can say
7:50
use the enhance button here to say uh
7:52
enhance this and enhance uh this prompt
7:55
and provide a better better uh structure
7:58
format. You know this is kind of more um
8:01
like a styling change that we're making
8:03
here. But if you wanted to kind of say,
8:04
I want you to enhance this to, you know,
8:06
respond this way or have this tone, then
8:09
you can automatically do that in here as
8:10
well.
8:12
So, we've now essentially have
8:14
capabilities to create these separate
8:17
agents within the builder and connect it
8:21
to different tools and settings. So,
8:23
what that means is you can determine the
8:26
level of reasoning. So, for example, one
8:28
agent you wanted to do high level of
8:30
thinking. you want you're solving a very
8:31
specific problem and the other you want
8:33
it to be very minimal and just execute
8:35
on the task at hand. Um you can connect
8:38
different tools. So if there's specific
8:40
functions, MCPS or vector stores, you
8:44
can do that as well. And you can also
8:46
transform how you want the output format
8:48
of the text to be. So in this instance,
8:50
for example, I can change this to say I
8:52
want this to be in a JSON format. And I
8:54
can add a schema to say in your response
8:57
just this is how you should respond. do
8:59
not even respond in regular text. But
9:01
for now, we're just going to do regular
9:02
text just because it's easier. And at
9:04
the same time, you can also connect it
9:06
to um different tools. In this case, I
9:10
connected to a vector store, which is a
9:12
set of documents I've created um as
9:15
context for the agent to reference.
9:19
Um and then from there, if it's not
9:22
existing customer and it's a new lead, I
9:24
have a sales agent lead. And this sales
9:27
agent lead right here again is helpful
9:30
and knowledgeable in capturing data
9:32
about this lead. It will ask them around
9:34
kind of what's your website URL, what's
9:36
your company name, what's your email,
9:39
how many visits do you get per uh per
9:40
month. Like let's say we're building an
9:41
analytics tool here and what are you
9:43
currently using? It'll gather that and
9:45
structure the data so that at this next
9:47
step you can pass it on to let's say
9:48
your database or a Slack notification or
9:50
add it to your CRM.
9:53
Any uh questions so far? No, take taking
9:56
it all in. Um, well, I mean, actually,
9:59
one quick question. The reason why you'd
10:01
want minimal reasoning versus advanced
10:04
reasoning, is that just from a speed and
10:07
cost perspective?
10:08
Exactly. So, the the the criteria around
10:12
minimal or high reasoning is entirely
10:14
dependent on the task at hand and what
10:16
you want the actual agent to do. So, do
10:19
you want the agent to solve a very
10:20
complex problem? Then you probably want
10:22
high reasoning. or do you want the agent
10:24
to just execute knowing that's going to
10:26
be a very simple task at hand because um
10:29
you know maybe in this instance because
10:30
it's a support agent I would probably
10:32
maybe do medium
10:34
but if it's a sales agent it's pretty
10:36
simple it's like just take the data and
10:38
ask them questions like
10:40
what's your company name there's no
10:41
thinking really required for that
10:44
cool
10:44
yeah cool my cat is just wants to be in
10:46
this spot
10:48
um and then basically uh if you wanted
10:51
to as a next step just for the for this
10:53
demo This is a lot of configuration. I'm
10:54
not going to do that. But you can
10:56
actually add an MCP. So say for example,
10:58
if you wanted to add HubSpot and update
11:01
your CRM, you can add that here. You can
11:03
authenticate, add your token, and then
11:05
connect that so that this agent, for
11:08
example, can pull contacts from your
11:09
HubSpot or push data as well to update
11:12
your leads list in there if it wanted
11:13
to.
11:14
Yeah. And if you don't know what an MCP
11:16
is, I have a whole video with Ross Mike.
11:19
I'll include it in the show notes
11:20
clearly explain what an MCP is. But in
11:23
in layman's terms, like what is it
11:25
quickly?
11:26
In layman's terms, an MCP is essentially
11:28
a new interface for LLMs to interact
11:30
with with external tools. Typically, web
11:33
apps use APIs to pull and push data. In
11:36
this instance, LLM use MCP, model
11:38
context protocol, to actually push and
11:40
pull data within LLMs.
11:41
And the MCPS that are available at
11:43
launch are the ones that you showed.
11:46
Yeah. So right now um we have kind of
11:49
the existing OpenAI connectors that are
11:52
like the official ones and then there's
11:53
some third party servers as well.
11:55
Hopefully over time we can get more of
11:56
the official MCPS in there.
11:58
Right. Intercom, customer service,
12:01
Shopify, ecom.
12:03
Yeah. Yeah. And uh at the end of this
12:05
I'll talk about kind of um how this
12:08
compares to Claude and kind of where
12:10
where there's opportunities for
12:12
improvement as well and kind of how this
12:13
differentiates.
12:14
Okay. Yeah, you'll keep it real for us
12:15
at the end of it.
12:16
Yeah, I'll keep it very real. I think
12:17
what's really interesting here as well
12:18
is, you know, typically when it comes to
12:20
AI workflows, especially for people that
12:22
are just have they're like on the uh
12:27
they're just getting started with AI
12:28
adoption and they're just getting
12:30
started with AI fluency. And AI fluency,
12:32
I think, is determined around kind of do
12:34
you understand how to prompt? Do you
12:36
understand how to give the right amount
12:37
of context? Can you take responsibility
12:39
for the output? understand that you need
12:41
to refine this agent constantly because
12:44
I think from experience working with a
12:46
lot of companies, I've seen that people
12:48
that have uh still early AI adopters or
12:52
like they're still uh like not they're
12:54
late adopters but early in their AI
12:56
fluency stage, they have issues with
13:00
building trust with agents with the
13:03
inputs with the outputs that they get.
13:05
And what that means is if the agent gets
13:08
it wrong once, they immediately lose
13:10
trust. And that comes down to, you know,
13:14
understanding how to prompt, how to give
13:15
the right amount of context, and knowing
13:17
that you have to iterate on this and you
13:18
can't get it right. Why I'm sharing this
13:20
is because this agent builder um has
13:24
guard rails in place to help you kind of
13:27
refine this process. So, you can
13:29
actually preview it in here if you
13:31
wanted to, and we'll show what a preview
13:32
of that looks like. But you can also
13:34
build guard rails to say okay like I
13:36
want you to hide personal information if
13:38
this comes through or I want you to
13:39
moderate this if there's anything that
13:41
harmful coming in or if someone tries to
13:42
jailbreak this or if it hallucinates.
13:44
Hallucinates is a big big big part of
13:46
this where you know as you use more
13:47
context agents performance degrade over
13:50
time. So you can actually implement
13:52
guard rails to ensure that your input
13:55
and your output is actually structured
13:56
the way you want it to be. So uh let's
Demo of support/lead agents
13:59
run an example of what this actual
14:01
workflow looks like. So, we're going to
14:02
click on preview and you can actually
14:04
test a preview in here and say, "Hi, I'm
14:06
interested
14:09
in a Humbolty demo." So, this is just an
14:12
example app that I have. And the
14:16
classifier is now going to determine if
14:18
this is an existing user or a new lead.
14:23
And its reasoning is saying, "Oh, like
14:25
this is uh
14:28
you know, this is the new lead." And
14:30
it's now asking me, can you share a few
14:32
details about your business? So I'll say
14:34
my website is called amirmxc.com,
14:36
company is amir, email is air example
14:39
whateverample.com
14:41
and I'm doing about 10k monthly visits.
14:45
Uh, and I'm using Google Analytics
14:49
for basic traffic. And what it's doing
14:53
now is it's pulling information around
14:55
the vector store that we added the files
14:57
and saying, "Okay, cool. I'm going to
14:59
recommend a plan based on their needs
15:01
and then also prompt them to book a demo
15:04
if they wanted to. So, it says, "Okay,
15:06
cool. We got your details based on 10K
15:08
visits and interest in heat maps and
15:10
funnels. Um, I recommend our our plus
15:12
plan to get started with. You can also
15:14
book a demo right here or get started
15:15
with a free trial. And if we wanted to,
15:17
we can have an MCP that pushes all this
15:19
data to our database or to Slack, which
15:21
sets a demo automatically or even just
15:23
like in through here creates an account
15:25
if we wanted to.
15:27
That's cool. Now that we have this
15:29
builder workflow built out, what's
15:31
interesting is that we can actually uh
15:33
get this incorporated into a chat UI
15:37
window. You can either use chatkit which
15:39
I talked about earlier which is a new
15:41
interface for you to actually uh embed
15:44
um chat bots into your website or you
15:46
can build your own custom agent SDK if
15:48
you wanted to. So you just have to paste
15:50
over the workflow ID and the API keys
15:52
that you have and you can build um yeah
15:55
build your own chatbot. So what does
15:57
that actually look like? Let's just in
16:00
make sure that we have everything set up
16:01
properly. We publish this and what's
16:04
really cool is we're now removing a lot
16:08
of developer dependency. What does that
16:10
mean? So if for example in a setting um
16:13
you have a customer support team that
16:15
has built this agentic workflow, they
16:17
can get this chatbot installed in their
16:19
site and make changes and not have to
16:22
rely on engineering team to actually
16:24
deploy that for them. It's all happening
16:26
live on the front end. So what that
16:28
actually means is say for example you
Integration with ChatKit to embed the chatbot on websites
16:30
have a website. We've now used chatkit
16:32
to integrate this on the front end. It's
16:34
just a script we've installed
16:36
and now we have a fully working chatbot
16:39
trained on our data and the multi- aent
16:42
workflow. If I wanted to come back and
16:44
change this workflow to add more agents
16:46
or add more tools um we can just publish
16:49
directly through from agent builder and
16:52
I don't have to go to the engineering
16:53
team and say hey can you deploy this for
16:55
me
16:56
and the cost of running this is just the
16:58
amount of tokens right
17:00
exactly you hook up your open API open
17:03
AI API keys and just your server
17:06
associated with it
17:09
cool so we essentially now have kind of
17:11
like a chatbot that can now accept
17:13
accept leads on a website. So, I can
17:15
just say uh I'm interested
17:18
in a demo. I have uh Google Analytics,
17:23
but I want Humbolytics
17:28
10K monthly visits. And this will now
17:33
determine that I'm actually a lead and
17:35
respond and um essentially say, "Hey,
17:37
let's let's get you booked in for a
17:39
demo. We got your information. Let's
17:40
proceed." And you can, you know, the the
17:43
agent builder has logs so you can track
17:45
all that.
17:46
Perfect. Yep.
17:49
Crazy.
17:50
So, it's pretty interesting. You can
17:53
also Yeah. If you wanted to have this
17:55
completely as a customer support bot so
17:56
that if you have issues, you can just
17:58
say, um, actually, you know, I'm an
18:01
existing customer. I'm an existing
18:02
customer actually. Or let's just start a
18:04
new chat. I'm an existing customer. Uh,
18:09
help me. add a web flow
18:14
site to track and hopefully it
18:17
determines that I'm actually an existent
18:18
customer and uh it'll give me um insight
18:21
on how to actually add it to how to
18:24
start tracking it. There you go.
18:28
So, we have essentially built a fully
18:32
working chatbot using contacts and rags
18:36
to first determine if you're a new
18:37
customer or a lead. if you're an
18:40
existing customer or a lead and then
18:41
either solve your inquiry if you have an
18:43
issue with the product or get your
18:45
information and get you set up. Um yeah,
18:48
so it's fully working and what's really
18:51
interesting is that you can actually
18:52
customize um the the widget as well
18:56
using the playground. So if you want to
18:58
kind of have disclaimers or composers um
19:00
it's fully customizable and it's really
19:02
simple to get set up with. Uh you can
19:04
just either use an embed code on your
19:06
website. Uh you just have to stand up a
19:09
server to get this work working or you
19:11
can kind of build a very custom agent.
19:12
Um uh fully working within your app if
19:16
you have an in-app experience you want
19:17
to have where you have a chatbot working
19:18
with it. Um yeah. So any uh what do you
19:22
think so far?
Differences between Agent Builder vs other alternatives
19:24
I mean someone's going to ask like okay
19:26
well why is this better than intercom or
19:30
a SAS product I can go and use? like why
19:32
do I need to create this myself?
19:35
I think that's a good question. So I
19:37
mean so first of all there's there's two
19:39
use cases here. If you want to build use
19:41
this internally um I think the multi-
19:43
aent builder right here is still um
19:46
there's still a lot of value out here,
19:48
right? where if you wanted to have a
19:49
multi- aent orchestration and say you
19:51
want to connect an MCP like Slack where
19:53
it sends information um that's still
19:55
like useful in a sense where you have
19:57
these backend automations with multiple
20:00
agents working together to get a task
20:01
done for you um now if you know I'd say
20:07
you are a startup midsize company and
20:10
you want to save on cost and you have
20:11
the engineer engineering capabilities
20:13
then using these agent builders to then
20:17
integrate with track chat kit to get it
20:19
on your app on your website could be a
20:20
huge timesaver in in the future or a
20:23
cost saver as well. Like there is a
20:25
learning curve and a um investment
20:27
initially but over time I think you
20:29
could have a lot of time savings and
20:30
cost savings as well.
20:31
I also think it's a little more a little
20:34
more custom. You can really really
20:36
fine-tune it exactly how you want it.
20:39
Right.
20:40
Exactly. Yeah. You have full control
20:42
over it. um you own it in a way like you
20:45
essentially own the workflow in the
20:46
system. Um there's a lot of great tools
Key Takeaways
20:48
like if you're looking for something out
20:49
of the box like you know Lindy and Gum
20:51
Loop they're all great tools but if you
20:53
want to build something more custom for
20:54
yourself then this is this is the way to
20:55
go.
20:56
Cool. Anything else?
20:59
Um and then yeah I think the the the you
21:01
know obviously the key the key takeaway
21:03
here is okay like you know what one what
21:06
are the key takeaways here?
21:08
Yeah,
21:08
it's a visual drag and drop tool. It's a
21:10
low barrier entry for non-technical
21:12
people. I think there's still some
21:13
dependency where you got to have some
21:14
technical knowledge, but I think the
21:16
multi- aent workflow is very
21:17
interesting. You know, in common times
21:19
you see people using one chat window for
21:22
like multiple tasks and you know that's
21:25
not the right way to do it. You want to
21:26
break up tasks into subtasks. Um I do
21:29
think the cloud code SDK is still
21:31
capable um based on the model and the
21:34
sub aent orchestration. The only
21:35
challenging thing is to get nontechnical
21:37
people playing with this. they can't use
21:39
a CLI like that scares them, you know.
21:42
So, what's interesting is we've taken
21:44
the capabilities of what these agent
21:46
workflows look like and we've built an
21:47
interface on top. People that are
21:49
already familiar with NAN or Zapier. Um,
21:53
you know, Cloud App is very similar like
21:56
in terms of the projects and MCP tools
21:58
you can build in it. Same thing with
21:59
like the projects in Chad GBT. Um, I'm
22:02
curious to see how kind of this evolves
22:04
over time where we have more uh MCP
22:06
capabilities,
22:07
right? Um
22:08
just just a quick note on that. So this
22:11
you you are right like the CLI the
22:13
terminal is daunting for people and it's
22:16
the equivalent I'm old enough to
22:18
remember using MS DOS
22:21
to access a computer which was basically
22:23
a terminal and computers didn't hit you
22:26
know mainstream adoption until there was
22:28
some graphical user interface on top of
22:30
it. Microsoft Windows uh or you know
22:34
Windows XP I think it was or or Windows
22:36
3.1.
22:37
So I think it's that's this moment in in
22:40
AI right we're putting we're putting
22:43
canvases on top of uh
22:47
you know sort of the hardcore technical
22:51
hood like the average person doesn't
22:52
want to be chilling in a terminal.
22:55
Exactly. Yeah. Yeah. Exactly. I think
22:57
you know as we think about the models
23:00
like there there's so much emphasis on
23:03
using LLM and agent workflows for
23:05
engineering and coding that the the
23:08
knowledge workers the nontechnical
23:09
people have been kind of left behind.
23:11
The experience is great for coding but
23:14
it's like but how do we cater this for
23:15
non people that actually want this kind
23:17
of use case which I think is a broader
23:19
use case as well. Um so you know a lot
23:22
of people the common questions they have
23:23
is like how do I actually get started
23:25
with this? How do I get started with
23:27
agent builder? So, it's available in
23:29
platform.openai.com.
23:31
Um, it's not too in the platform side of
23:34
things. Um, I would say to get started,
23:38
think about the use case and what it is
23:40
that you actually want to achieve here.
23:41
You know, for me it was like it'd be
23:42
really cool to just have my own customer
23:45
support agent so I don't have to pay
23:46
$150 a month and have it do exactly what
23:49
it's currently doing right now, but also
23:51
be able to actually capture leads and I
23:52
own it. I control it and I can build
23:54
more, you know, um, integrations
23:56
afterwards. Then you work backwards. You
23:58
say, okay, what does this existing
23:59
workflow look like and how do we
24:01
actually build multiple agents that can
24:03
play a part in this and have them be
24:04
very specialized? The next step is, I
24:07
think, building your data context,
24:09
right? capture your data, figure out
24:12
what structure your data should look
24:13
like, where you want to store it, what
24:14
should the context be, clean up your
24:16
data, and then add it as a vector store
24:18
as a as a file to for your agent to
24:20
reference. And I showed it in the in the
24:22
agent builder how you can actually
24:24
reference that. Then, you know, the goal
24:26
is to try to use as little context as
24:28
possible to get the most out of it.
24:30
Context has a huge impact on performance
24:32
and it degrades it over time. And then
24:34
if you need to use multiple agent
24:36
workflows like we like you saw
24:38
classifier then we have the sales sales
24:40
lead then we have the customer support
24:42
bot specify the roles and then from
24:44
there determine if you need external
24:45
tools and MC you know like MCPS or web
24:48
search um I would say claude is
24:50
definitely ahead of the game when it
24:51
comes to MCPs um they're the ones that
24:55
invented that yeah they invented it
24:57
right so there's a lot more directory
24:59
and uh the directory is a lot more
25:01
capable and there's a lot more features
25:02
available when it comes to MCPS cloud,
25:05
you know, open AI's got to step it up.
25:06
They gota they got they got they got to
25:08
make it easier to to get more MCP
25:10
capabilities in there because that's the
25:12
most important thing. Um, and yeah, I uh
25:14
I hope I hope it was helpful in terms of
25:16
just kind of what came out and how you
25:17
can get started.
25:18
So,
25:20
uh, yeah. So, this is like super clear
25:22
and that's why I wanted to have you on
25:23
to just break this down. Um, for the
Opportunities for founders
25:26
average founder who's listening to this,
25:29
like where are the opportunities? like
25:31
what should they be thinking about? So
25:34
the average founder that is uh listening
25:37
to this where are the opportunities two
25:39
parts I think the unrelated but open
25:42
AAI's app capabilities that's now
25:44
available in Chad GBT is huge right it's
25:47
like we're now seeing Chad GPT as a new
25:50
distribution and new to your point
25:52
interface layer to have it interact with
25:54
your app so that's I would say from a
25:57
growth standpoint use apps as a
26:00
distribution channel
26:02
specific specifically with agent builder
26:04
and the chatk UI.
26:07
Get this in front of your non-technical
26:09
team members. Give this to your product
26:11
managers. Give this to your customer
26:12
support team. Give this to your go to
26:14
market sales team. Give them an engineer
26:16
to support them with building out the
26:17
MCPS and workflows and standing up a
26:20
server and see what they can create with
26:22
this. Enable them to save time
26:25
and tell them to share this video and
26:28
like and comment so that it spreads to
26:30
the world. Yes, exactly.
26:33
Amir, thanks for coming on and breaking
26:35
it down so clearly. I'll include links
26:37
to follow Amir uh where he shares
26:40
knowledge on all all this sort of stuff
26:42
in the show notes. Uh appreciate you
26:44
being generous with your sauce and uh so
26:47
clear in your thinking.
26:49
Happy to help.
26:50
Later.
26:50
Thank you. Thank you sir.

