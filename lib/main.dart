import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const String _apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://hamrah-dana.onrender.com',
);

void main() => runApp(const HamrahDanaApp());

class HamrahDanaApp extends StatelessWidget {
  const HamrahDanaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'همراه دانا',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF101522),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C8CFF),
          brightness: Brightness.dark,
        ),
        fontFamily: 'Roboto',
      ),
      home: const ChatPage(),
    );
  }
}

class ChatMessage {
  const ChatMessage(this.text, this.fromUser);
  final String text;
  final bool fromUser;
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = <ChatMessage>[
    const ChatMessage('سلام! من همراه دانا هستم. چه کمکی از دستم برمیاد؟', false),
  ];
  bool _loading = false;

  Future<void> _send() async {
    final String message = _controller.text.trim();
    if (message.isEmpty || _loading) return;

    setState(() {
      _messages.add(ChatMessage(message, true));
      _loading = true;
      _controller.clear();
    });
    _scrollToBottom();

    try {
      final http.Response response = await http
          .post(
            Uri.parse('$_apiBaseUrl/chat'),
            headers: const <String, String>{
              'Content-Type': 'application/json; charset=utf-8',
              'Accept': 'application/json',
            },
            body: jsonEncode(<String, String>{'message': message}),
          )
          .timeout(const Duration(seconds: 100));

      if (!mounted) return;

      Map<String, dynamic>? data;
      try {
        final Object? decoded = jsonDecode(response.body);
        if (decoded is Map<String, dynamic>) data = decoded;
      } on FormatException {
        data = null;
      }

      if (response.statusCode == 200) {
        final Object? answer = data?['answer'];
        final String answerText = answer is String && answer.trim().isNotEmpty
            ? answer.trim()
            : 'پاسخی از سرور دریافت شد، اما متن پاسخ خالی بود.';
        _addAssistantMessage(answerText);
      } else if (response.statusCode == 503) {
        _addAssistantMessage(
          'سرویس هوش مصنوعی فعلاً آماده نیست. تنظیمات کلید API سرور باید بررسی شود.',
        );
      } else if (response.statusCode == 502 || response.statusCode == 504) {
        _addAssistantMessage(
          'ارتباط سرور با سرویس هوش مصنوعی دچار مشکل شد. لطفاً کمی بعد دوباره امتحان کن.',
        );
      } else {
        _addAssistantMessage(
          'سرور پاسخ موفق نداد (کد ${response.statusCode}).',
        );
      }
    } on TimeoutException {
      if (mounted) {
        _addAssistantMessage(
          'پاسخ‌گویی بیش از حد طول کشید. وضعیت اینترنت و روشن بودن سرویس سرور را بررسی کن.',
        );
      }
    } on SocketException {
      if (mounted) {
        _addAssistantMessage(
          'به سرور دسترسی پیدا نشد. اتصال اینترنت یا آدرس سرور را بررسی کن.',
        );
      }
    } on http.ClientException {
      if (mounted) {
        _addAssistantMessage(
          'ارتباط شبکه برقرار نشد. لطفاً اینترنت دستگاه را بررسی کن.',
        );
      }
    } catch (_) {
      if (mounted) {
        _addAssistantMessage(
          'هنگام دریافت پاسخ خطای غیرمنتظره‌ای رخ داد. دوباره تلاش کن.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
        _scrollToBottom();
      }
    }
  }

  void _addAssistantMessage(String text) {
    if (!mounted) return;
    setState(() => _messages.add(ChatMessage(text, false)));
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF171F31),
        title: const Row(
          children: <Widget>[
            CircleAvatar(
              backgroundColor: Color(0xFF6C8CFF),
              child: Icon(Icons.auto_awesome, color: Colors.white),
            ),
            SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  'همراه دانا',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  'دستیار آموزشی برق و الکترونیک',
                  style: TextStyle(fontSize: 11, color: Colors.white70),
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: <Widget>[
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (BuildContext context, int index) {
                final ChatMessage item = _messages[index];
                return Align(
                  alignment: item.fromUser
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    constraints: const BoxConstraints(maxWidth: 310),
                    margin: const EdgeInsets.symmetric(vertical: 7),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: item.fromUser
                          ? const Color(0xFF425FC2)
                          : const Color(0xFF202B40),
                      borderRadius: BorderRadius.circular(18),
                    ),
                    child: Text(
                      item.text,
                      textDirection: TextDirection.rtl,
                      style: const TextStyle(fontSize: 15, height: 1.6),
                    ),
                  ),
                );
              },
            ),
          ),
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(8),
              child: Text('همراه دانا در حال پاسخ‌گویی است...'),
            ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
              child: Row(
                children: <Widget>[
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      textDirection: TextDirection.rtl,
                      minLines: 1,
                      maxLines: 4,
                      onSubmitted: (_) => _send(),
                      decoration: InputDecoration(
                        hintText: 'پیامت رو بنویس...',
                        filled: true,
                        fillColor: const Color(0xFF202B40),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 18,
                          vertical: 12,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _loading ? null : _send,
                    icon: const Icon(Icons.send_rounded),
                    style: IconButton.styleFrom(
                      backgroundColor: const Color(0xFF6C8CFF),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
