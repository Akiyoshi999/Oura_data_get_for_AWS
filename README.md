# Oura_data_get

## プログラムの概要

Oura ring の本日のデータ、1 週間分のデータの平均値を取得し、取得したスコアを LINE で通知する。

## 作成の動機

Oura ring は自分の睡眠状態や健康状態を数値化してくれる便利なものだが、各日付毎のスコアしか分からない上にアプリを開かないとスコアが確認できないのが面倒。
そこでスコアを LINE に送信することによって、LINE で本日のスコアや 1 週間分の平均スコアを確認したいと思い作成しました。
また、Cloud 環境で構築したいと考えて AWS 環境で作成した。

## 事前準備

- Oura の Personal Access Token を作成すること
  https://cloud.ouraring.com/personal-access-tokens

- LINE notify を登録し Token を作成すること
  https://notify-bot.line.me/ja/

## 使い方

1. 事前準備で使用した token の値や 1 週間のデータをまとめて取得したい曜日をパラメータストアに追記する。
1. 毎日 10 時頃に Event bridge を経由して Lambda が実行される。 LINE に本日のスコアが送信される。1 週間のスコアを取得している曜日であれば、1 週間のスコアの平均点も送信される。

## 構成

![architecture dio drawio](https://github.com/Akiyoshi999/Oura_data_get_for_AWS/assets/47466766/a055cf97-1ecb-40d8-8703-cd332ba0d671)

## 使用画面

![](https://raw.githubusercontent.com/wiki/Akiyoshi999/Oura_data_get/images/oura_get_photo.PNG)
