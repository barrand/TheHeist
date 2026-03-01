import 'dart:math';
import 'package:flutter/material.dart';
import 'package:the_heist/core/theme/app_colors.dart';
import 'package:the_heist/models/minigame.dart';
import 'package:the_heist/widgets/minigames/shared_ui.dart';

/// Match stolen items to the correct buyers. One wrong match = fail.
class ItemMatchingMinigame extends StatefulWidget {
  final MinigameDifficulty difficulty;

  const ItemMatchingMinigame({super.key, required this.difficulty});

  @override
  State<ItemMatchingMinigame> createState() => _ItemMatchingMinigameState();
}

class _StolenItem {
  final int id;
  final String name;
  final IconData icon;
  final Color color;
  _StolenItem(this.id, this.name, this.icon, this.color);
}

class _Buyer {
  final int id;
  final String name;
  final int wantsItemId; // which _StolenItem.id this buyer wants
  _Buyer(this.id, this.name, this.wantsItemId);
}

class _ItemMatchingMinigameState extends State<ItemMatchingMinigame> {
  late List<_StolenItem> _items;
  late List<_Buyer> _buyers;
  late int _pairCount;
  late int _maxStrikes;
  final Map<int, int> _matches = {}; // itemId -> buyerId
  int _strikes = 0;
  int? _selectedItemId;
  bool _gameWon = false;
  bool _gameOver = false;
  String _feedback = '';
  late Random _random;

  // Pool of 13 items - each difficulty uses a different non-overlapping slice
  // Each item aligns with its matching company (same index)
  static final List<_StolenItem> _allItems = [
    _StolenItem(0, 'Oil Painting', Icons.palette, Colors.amber),
    _StolenItem(1, 'Diamond Ring', Icons.diamond, Colors.cyan),
    _StolenItem(2, 'Vintage Watch', Icons.watch, Colors.teal),
    _StolenItem(3, 'Confidential Files', Icons.folder, Colors.orange),
    _StolenItem(4, 'Bronze Statue', Icons.account_balance, Colors.brown),
    _StolenItem(5, 'Gold Bars', Icons.monetization_on, Colors.yellow.shade700),
    _StolenItem(6, 'Pearl Necklace', Icons.circle, Colors.white70),
    _StolenItem(7, 'Stamp Album', Icons.mail, Colors.green),
    _StolenItem(8, 'Ming Vase', Icons.inventory_2, Colors.red.shade900),
    _StolenItem(9, 'Rare Coins', Icons.currency_bitcoin, Colors.amber.shade700),
    _StolenItem(10, 'Rare Book', Icons.menu_book, Colors.indigo),
    _StolenItem(11, 'Fur Coat', Icons.checkroom, Colors.brown.shade400),
    _StolenItem(12, 'Wine Crate', Icons.liquor, Colors.deepPurple),
  ];

  // Companies that logically deal in each item type (aligned by index)
  static final List<String> _buyerNames = [
    'Metro Gallery', 'Brilliant Acquisitions', 'Chrono Trade',
    'Black Box Ltd', 'Heritage Sculpture Co', 'Bullion Exchange',
    'Lustre Holdings', 'First Post Co', 'Antique Row',
    'Mint Condition Ltd', 'Archive Partners', 'Atelier Luxe', 'Cellar Direct',
  ];

  @override
  void initState() {
    super.initState();
    _random = Random();
    _resetGame();
  }

  void _resetGame() {
    setState(() {
      _gameWon = false;
      _gameOver = false;
      _feedback = '';
      _matches.clear();
      _strikes = 0;
      _selectedItemId = null;

      int startIndex;
      switch (widget.difficulty) {
        case MinigameDifficulty.easy:
          _pairCount = 3;
          _maxStrikes = 1;
          startIndex = 0;
          break;
        case MinigameDifficulty.medium:
          _pairCount = 4;
          _maxStrikes = 0;
          startIndex = 3;
          break;
        case MinigameDifficulty.hard:
          _pairCount = 6;
          _maxStrikes = 0;
          startIndex = 7;
          break;
      }

      // Each difficulty uses a different slice - no duplicates across levels
      final slice = _allItems.sublist(startIndex, startIndex + _pairCount);
      final namesSlice = _buyerNames.sublist(startIndex, startIndex + _pairCount);
      _items = List.from(slice);
      _buyers = List.generate(
        _pairCount,
        (i) => _Buyer(i, namesSlice[i], slice[i].id),
      );
      _items = List.from(_items)..shuffle(_random);
      _buyers = List.from(_buyers)..shuffle(_random);
    });
  }

  void _onItemTap(int itemId) {
    if (_gameOver || _gameWon) return;
    if (_matches.containsKey(itemId)) return; // already matched

    setState(() {
      _selectedItemId = _selectedItemId == itemId ? null : itemId;
      _feedback = _selectedItemId != null ? 'Select a buyer' : '';
    });
  }

  void _onBuyerTap(int buyerId) {
    if (_gameOver || _gameWon) return;
    if (_selectedItemId == null) return;
    if (_matches.values.contains(buyerId)) return; // buyer already taken

    final buyer = _buyers.firstWhere((b) => b.id == buyerId);
    final correct = buyer.wantsItemId == _selectedItemId;

    setState(() {
      if (correct) {
        _matches[_selectedItemId!] = buyerId;
        _feedback = '✓ Sold!';
        if (_matches.length >= _pairCount) {
          _gameWon = true;
        }
      } else {
        _strikes++;
        _feedback = 'Wrong buyer!';
        if (_strikes > _maxStrikes) {
          _gameOver = true;
        }
      }
      _selectedItemId = null;

      if (!_gameOver && !_gameWon) {
        Future.delayed(const Duration(milliseconds: 800), () {
          if (mounted) setState(() => _feedback = '');
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_gameWon) {
      return buildWinScreen('DEALS DONE!', Icons.handshake, _resetGame);
    }
    if (_gameOver) {
      return buildFailScreen(_resetGame);
    }

    return Column(
      children: [
        buildStatsBar(
          'Sold: ${_matches.length} / $_pairCount',
          _maxStrikes > 0 ? 'Strikes: $_strikes / $_maxStrikes' : 'No mistakes!',
        ),
        const SizedBox(height: 12),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            'Tap item, then tap the buyer who wants it',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
          ),
        ),
        SizedBox(
          height: 36,
          child: Center(
            child: _feedback.isNotEmpty
                ? Text(
                    _feedback,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _feedback.contains('✓') ? AppColors.success : AppColors.danger,
                    ),
                  )
                : const SizedBox.shrink(),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Items
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: _items.map((item) => _buildItem(item)).toList(),
                  ),
                  const SizedBox(width: 16),
                  // Buyers
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: _buyers.map((buyer) => _buildBuyer(buyer)).toList(),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildItem(_StolenItem item) {
    final isMatched = _matches.containsKey(item.id);
    final isSelected = _selectedItemId == item.id;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: GestureDetector(
        onTap: () => _onItemTap(item.id),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: 90,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
          decoration: BoxDecoration(
            color: isMatched
                ? AppColors.success.withValues(alpha: 0.2)
                : (isSelected ? item.color.withValues(alpha: 0.4) : AppColors.bgSecondary),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isMatched ? AppColors.success : (isSelected ? item.color : AppColors.borderSubtle),
              width: isSelected ? 3 : 2,
            ),
            boxShadow: isSelected
                ? [BoxShadow(color: item.color.withValues(alpha: 0.5), blurRadius: 12, spreadRadius: 2)]
                : [],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                item.icon,
                color: isMatched ? AppColors.success : item.color,
                size: 28,
              ),
              const SizedBox(height: 4),
              Text(
                item.name,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: isMatched ? AppColors.success : AppColors.textPrimary,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBuyer(_Buyer buyer) {
    final isMatched = _matches.values.contains(buyer.id);
    int? matchedItemId;
    for (final e in _matches.entries) {
      if (e.value == buyer.id) {
        matchedItemId = e.key;
        break;
      }
    }
    final matchedItem = matchedItemId != null ? _items.firstWhere((i) => i.id == matchedItemId!) : null;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: GestureDetector(
        onTap: () => _onBuyerTap(buyer.id),
        child: Container(
          width: 100,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
          decoration: BoxDecoration(
            color: isMatched ? AppColors.success.withValues(alpha: 0.2) : AppColors.bgSecondary,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isMatched ? AppColors.success : AppColors.borderSubtle,
              width: 2,
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (isMatched && matchedItem != null)
                Icon(matchedItem.icon, color: AppColors.success, size: 24)
              else
                Icon(Icons.person_outline, color: AppColors.textSecondary, size: 24),
              const SizedBox(height: 4),
              Text(
                buyer.name,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: isMatched ? AppColors.success : AppColors.textSecondary,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
