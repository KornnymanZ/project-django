import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  String? _token;
  bool _isAuthenticated = false;

  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;

  final GoogleSignIn _googleSignIn = GoogleSignIn(
    clientId: '318140156004-h45knkerb3uoti4bms4qdtpabv2l4k8n.apps.googleusercontent.com',
    scopes: ['email', 'profile'],
  );

  Future<bool> loginWithGoogle() async {
    try {
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) return false;

      final googleAuth = await googleUser.authentication;
      final idToken = googleAuth.idToken;

      if (idToken == null) return false;

      final response = await ApiService.post('api/auth/google/', {
        'id_token': idToken,
      });

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['access'];
        _isAuthenticated = true;

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('jwt_token', _token!);

        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Google Native Login Exception: $e');
      return false;
    }
  }

  Future<void> logout() async {
    _token = null;
    _isAuthenticated = false;
    await _googleSignIn.signOut();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    notifyListeners();
  }

  Future<void> tryAutoLogin() async {
    final prefs = await SharedPreferences.getInstance();
    if (!prefs.containsKey('jwt_token')) return;

    _token = prefs.getString('jwt_token');
    _isAuthenticated = true;
    notifyListeners();
  }
}
