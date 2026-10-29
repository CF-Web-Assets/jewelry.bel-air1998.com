#!/usr/bin/perl

#┌─────────────────────────────────
#│ DREAM COUNTER v3.31 (2002/08/04)
#│ Copyright(C) Kent Web 2002
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────
$ver= 'Dream Counter v3.31';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このスクリプトはフリーソフトです。このスクリプトを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────
#
# [タグの書き方の例] (*** はログファイル名)
#
#  ・カウンタ <img src="http://～～/count/dream.cgi?id=***">
#  ・時刻表示 <img src="http://～～/count/dream.cgi?mode=time">
#  ・カレンダ <img src="http://～～/count/dream.cgi?mode=date">
#  ・ファイルの更新時間
#             <img src="http://～～/count/dream.cgi?file=/home/～/index.html">
#             [注意] --> /home/～/index.htmlの部分はフルパスを指定
#
#  * 応用例 (ID名を index と仮定)
#    1.画像を変更するとき：(以下はgif2ディレクトリの画像指定例)
#      <img src="http://～～/count/dream.cgi?id=index&gif=2">
#    2.数字をランダムに表示するとき：
#      <img src="http://～～/count/dream.cgi?mode=rand">
#    3.カウンタ桁数を７桁にするとき：
#      <img src="http://～～/count/dream.cgi?id=index&fig=7">
#
#  * チェックモード (mode=check という引数をつけて呼び出す）
#    http://～～/dream.cgi?mode=check
#
# [ ディレクトリ構成例 (かっこ内はパーミッション) ]
#
#  public_html / index.html(ここにカウンタ等を表示)
#       |
#       +-- count / dream.cgi  [755]
#             |     gifcat.pl  [644]
#             |     drinit.cgi [644]
#             |     drmgr.cgi  [755]
#             |
#             +-- data [777] / index.dat [666]
#             |                xxxxx.dat [666}
#             |                   :
#             |                   :
#             |
#             +-- lock [777] /
#             |
#             +-- gif1 / 0.gif .. 9.gif, a.gif, p.gif, c.gif, d.gif
#             |
#             +-- gif2 / 0.gif .. 9.gif, a.gif, p.gif, c.gif, d.gif
#                  :
#

# IIS対策
if ($ENV{'SERVER_SOFTWARE'} =~ /IIS/i) {
	local($chdir) = $0;
	$chdir =~ s/[^\\]*$//;
	chdir($chdir);
}

# ライブラリ/設定ファイル取込
require './gifcat.pl';
require './drinit.cgi';

# デコード処理
$string = &decode;
$in{'id'}  =~ s/\W//g;
$in{'fig'} =~ s/\D//g;
if ($in{'fig'} > $maxfig) { $in{'fig'} = $maxfig; }

# チェックモード
if ($mode eq "check") {	&check; }

# 他サイトからのアクセスを排除
if ($base_url) {
	$ref = $ENV{'HTTP_REFERER'};
	$ref =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	if ($ref !~ /$base_url/i) { &error; }
}

# 画像ディレクトリを定義
if ($in{'gif'}) {
	$in{'gif'} =~ s/\D//g;
	$gifdir =~ s/(.*)\d+\/$/$1$in{'gif'}\//g;
}

## ランダムモード
if (!$string || $mode eq 'rand') {
	srand;
	if (!$in{'fig'}) { $in{'fig'} = 5; }
	foreach (1 .. $in{'fig'}) {
		$rand = int(rand(10));
		$count .= $rand;
	}
	&count_view($count);
}

## カウンタ処理
elsif ($in{'id'} ne "") { &counter; }

## 時間処理
elsif ($mode eq "time") {
	# 時間を取得
	&get_time;

	if ($in{'type'} == 24) { $count = $hour . 'c' . $min; }
	else {
		if ($hour >= 12) {
			$hour = sprintf("%02d", $hour-12);
			$head = 'p';
		} else { $head = 'a'; }

		$count = $head . $hour . 'c' . $min;
	}
	&count_view($count);
}
## カレンダ処理
elsif ($mode eq "date") {
	# 時間を取得
	&get_time;

	if ($in{'year'} == 4) {
		$year += 1900;
		$count = $year . 'd' . $mon . 'd' . $mday;
	} else {
		$year = sprintf("%02d", $year-100);
		$count = $year . 'd' . $mon . 'd' . $mday;
	}
	&count_view($count);
}

## 更新時間表示処理
elsif ($in{'file'}) {
	# ファイルがなければエラー
	unless (-e $in{'file'}) { &error; }

	# 更新日数を取得
	($mtime) = (stat($in{'file'}))[9];

	# 更新時間
	&get_time($mtime);
	$year += 1900;

	# スラッシュ "/" がなければダッシュ "-" で代用
	$slush = $gifdir . 's.gif';
	if (-e $slush) { $s = 's'; } else { $s = 'd'; }

	$count = $year . $s . $mon . $s . $mday . 'd' . $hour . 'c' . $min;
	&count_view($count);
}

## ファイルサイズ数表示処理
elsif ($in{'size'}) {
	# ファイルがなければエラー
	unless (-e $in{'size'}) { &error; }

	# サイズ数を取得 (bytes)
	($size) = (stat($in{'size'}))[7];

	# 単位変換（四捨五入）
	if ($in{'p'} eq 'k') { $size = int(($size / 1024)+0.5); }
	elsif ($in{'p'} eq 'm') { $size = int(($size / 1048576)+0.5); }

	&count_view($size);
}

## 強制表示（数字のみ）
elsif ($in{'num'} ne "") {
	$in{'num'} =~ s/\D//g;
	&count_view($in{'num'});
}

## 他の引数だとエラー
else { &error; }

#---------------#
#  GIF出力処理  #
#---------------#
sub count_view {
	local($count) = $_[0];
	@char = split(//, $count);
	@image=();
	foreach (@char) { push(@image,"$gifdir$_\.gif"); }

	print "Content-type: image/gif\n\n";
	binmode(STDOUT);
	print &gifcat'gifcat(@image);
	exit;
}

#----------------#
#  カウンタ処理  #
#----------------#
sub counter {
	# ログを定義
	$logfile = "$datadir$in{'id'}\.dat";

	# ログの存在をチェック
	unless(-e $logfile) {
		# ログ生成 [なし] ならプログラムを終了
		if ($id_creat == 0) { &error; }

		# ログ生成 [あり] ならログを生成
		else {
			open(OUT,">$logfile") || &error;
			print OUT "0";
			close(OUT);

			# パーミッションを 666 へ
			chmod (0666,"$logfile");
		}
	}

	# デフォルト桁数を定義
	if ($in{'fig'} eq "") { $in{'fig'} = 5; }

	# IPアドレスを取得
	$addr = $ENV{'REMOTE_ADDR'};

	# ロック開始
	if ($lockkey) {
 		$lockfile = "$lockdir$in{'id'}\.lock";
		&lock;
	}

	# 記録ファイルから読み込み
	open(IN,"$logfile") || &error;
	$data = <IN>;
	close(IN);

	# 前バージョン変換処理
	if ($data =~ /<>/) { ($daykey, $data) = split(/<>/, $data); }

	# 記録ファイルを分解
	($count, $ip) = split(/:/, $data);

	# IPチェック
	$flag=0;
	if ($ip_chk && $addr eq $ip) { $flag=1; }

	# ログ更新
	if (!$flag) {
		# カウントアップ
		$count++;

		# ファイルをフォーマット
		if ($ip_chk) { $data = "$count\:$addr"; }
		else { $data = $count; }

		# 記録ファイルを更新する
		if ($rename) { &tmp2log($data); }
		else {
			open(OUT,">$logfile") || &error;
			print OUT $data;
			close(OUT);
		}
	}

	# ロック解除
	&unlock if ($lockkey);

	while (length($count) < $in{'fig'}) { $count = '0' . $count; }
	&count_view($count);
}

#--------------#
#  時間を取得  #
#--------------#
sub get_time {
	local($time) = @_;

	$ENV{'TZ'} = "JST-9";
	$time = time if (!$time);
	($min,$hour,$mday,$mon,$year) = (localtime($time))[1..5];

	$mon  = sprintf("%02d", $mon+1);
	$hour = sprintf("%02d", $hour);
	$min  = sprintf("%02d", $min);
	$mday = sprintf("%02d", $mday);
}

#--------------#
#  エラー処理  #
#--------------#
sub error {
	local(@err, $bin);
	&unlock if ($lockflag);
	unlink($tmpfile) if (-e $tmpfile);

	if ($_[0] eq 'rename') {
		@err = ('47','49','46','38','39','61','4b','00','0e','00','80','00','00','00','00','00','ff','ff','ff','21', 'f9','04','01','00','00','01','00','2c','00','00','00','00','4b','00','0e','00','00','02','73','8c', '8f','a9','cb','ed','0f','a3','9c','b4','da','8b','2d','d8','60','6e','d3','25','dc','97','55','24', '09','7d','e8','71','86','a5','d4','82','2d','27','8f','62','38','d7','28','1d','d8','3c','cf','72', 'c9','7a','9d','58','50','11','53','15','71','4b','a2','53','f9','14','ae','10','50','e7','f1','f6', '6b','1a','87','d0','ae','54','a8','b3','ae','a6','51','5d','53','4c','f3','12','81','e8','f2','d6', '4a','5d','9e','87','6e','ad','7d','91','bc','c3','f7','74','75','be','0e','18','b7','93','c6','74', '63','c8','65','34','73','97','f3','d2','e8','f8','08','09','59','00','00','3b');
	} else {
		@err = ('47','49','46','38','39','61','2d','00','0f','00','80','00','00','00','00','00','ff','ff','ff','2c', '00','00','00','00','2d','00','0f','00','00','02','49','8c','8f','a9','cb','ed','0f','a3','9c','34', '81','7b','03','ce','7a','23','7c','6c','00','c4','19','5c','76','8e','dd','ca','96','8c','9b','b6', '63','89','aa','ee','22','ca','3a','3d','db','6a','03','f3','74','40','ac','55','ee','11','dc','f9', '42','bd','22','f0','a7','34','2d','63','4e','9c','87','c7','93','fe','b2','95','ae','f7','0b','0e', '8b','c7','de','02','00','3b');
	}

	print "Content-type: image/gif\n\n";
	foreach (@err) {
		$bin = pack('C*',hex($_));
		print $bin;
	}
	exit;
}

#------------------------#
#  ログ更新：rename関数  #
#------------------------#
sub tmp2log {
	local($data) = @_;

	# 一時ファイルを定義
	$proc = "$$";
	if ($proc eq "") {
		srand;
		$proc = int(rand(10000000));
	}
	$tmpfile = "$lockdir$proc\.tmp";

	# 一時ファイルに書き出し
	open(TMP,"> $tmpfile") || &error;
	print TMP $data;
	close(TMP);

	# 正規ログへリネーム
	rename ($tmpfile, $logfile) || &error('rename');
	chmod (0666, $logfile);
}

#------------------#
#  チェックモード  #
#------------------#
sub check {
	local($flag1, $flag2, @file);

	&header;
	print "<h2>Check Mode</h2>\n<UL>\n";

	# データディレクトリ
	print "<LI>データディレクトリ：$datadir\n";
	if (-d $datadir) {
		$flag1=1;
		print "<LI>データディレクトリのパス：OK\n";
	} else {
		$flag1=0;
		print "<LI>データディレクトリのパス：NG → $datadir\n";
	}

	if (-r $datadir && -w $datadir && -x $datadir) {
		print "<LI>データディレクトリのパーミッション：OK\n";
	} else {
		print "<LI>データディレクトリのパーミッション：NG → $datadir\n";
	}

	# 他サイトからのアクセス制限
	print "<LI>他サイトからのアクセス制限：";
	if ($base_url) { print "あり → $base_url\n"; }
	else { print "なし\n"; }

	# ロックディレクトリ
	print "<LI>ロック形式：";
	if ($lockkey == 0) { print "ロック設定なし\n"; }
	else {
		if ($lockkey == 1) { print "symlink\n"; }
		else { print "mkdir\n"; }
		print "<LI>ロックディレクトリ：$lockdir\n";

		if (-d $lockdir) { print "<LI>ロックディレクトリのパス：OK\n"; }
		else { print "<LI>ロックディレクトリのパス：NG → $lockdir\n"; }

		if (-r $lockdir && -w $lockdir && -x $lockdir) {
			print "<LI>ロックディレクトリのパーミッション：OK\n";
		} else {
			print "<LI>ロックディレクトリのパーミッション：NG → $lockdir\n";
		}
	}

	# rename関数
	@YN = ("なし", "あり");
	print "<LI>rename関数：$YN[$rename]\n";

	# 画像ディレクトリのパス確認
	if (-d $gifdir) { print "<LI>$gifdir : 画像ディレクトリのパス : OK! \n"; }
	else { print "<LI>$gifdir : 画像ディレクトリがありません\n"; }

	# 画像チェック
	foreach ("0".."9", "a", "p", "c", "d") {
		if (-e "$gifdir$_\.gif") { print "<LI>$_ : 画像OK \n"; }
		else { print "<LI>$_ : 画像がありません\n"; }
	}

	# 画像連結
	print "<LI>画像連結テスト → <img src=\"$dream?num=0123456789\">\n";

	# ログファイル検索
	if ($flag1) {
		@file = &datadir;
		$flag2=0;
		foreach (@file) {
			$datfile = "$datadir$_";
			if (-r $datfile && -w $datfile) {
				print "<LI>ログ $_ : パーミッションOK \n";
			} else { print "<LI>ログ $_ : パーミッション<b>NG</b> \n"; }
			$flag2=1;
		}
		if (!$flag2) { print "<LI>ログファイルが存在しません\n"; }
	}

	# 著作権表示：削除改変禁止
	print <<"EOM";
</UL>
<div align="right" style="font-size:12px;font-family:verdana">Copyright (C) 
<a href="http://www.kent-web.com/" style="text-decoration:none">KENT WEB</a> 2002<br>
<b>$ver</b></div>
</body></html>
EOM
	exit;
}

__END__

