from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty, StringProperty, ListProperty, DictProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.button import Button
import webbrowser
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.textinput import TextInput
import requests
import threading
import logging
from kivy.uix.image import Image
from kivy.core.window import Window


logging.basicConfig(level=logging.DEBUG)

# 멜론 API로부터 아티스트 정보와 노래 정보를 추출하는 모듈을 임포트합니다.
import melon_extract_artist_id as artist_id_module
import melon_extract_song_info_with_artist_id as song_info_module

# 한글 폰트를 적용한 라벨 클래스를 정의합니다.
class KoreanLabel(Label):
    def __init__(self, **kwargs):
        super(KoreanLabel, self).__init__(**kwargs)
        self.font_name = './nanayang.ttf'
        self.text_size = self.size  # 텍스트 사이즈를 위젯의 크기에 맞춤
        self.halign = 'left'  # 좌측 정렬
        self.valign = 'middle'  # 중앙 정렬
        self.bind(size=self._update_text_size)
        self.font_size = 60
    
    def _update_text_size(self, *args):
        self.text_size = (self.width, self.height)

# 선택 시 배경색이 변경되는 라벨 클래스를 정의합니다.
class SelectableLabel(ButtonBehavior, Label):
    selected = BooleanProperty(False)  # 선택 상태를 나타내는 속성입니다.
    index = StringProperty()  # 각 라벨에 고유 인덱스 할당
    pressing = BooleanProperty(False)  # 눌림 상태를 나타내는 속성

    def __init__(self, **kwargs):
        super(SelectableLabel, self).__init__(**kwargs)
        self.font_name = './nanayang.ttf'
        self.text_size = self.size  # 텍스트 사이즈를 위젯의 크기에 맞춤
        self.halign = 'left'  # 좌측 정렬
        self.valign = 'middle'  # 중앙 정렬
        self.bind(size=self._update_text_size, selected=self.update_visuals)
        self.font_size = 60
        self.update_visuals()  # 초기 시각적 상태 업데이트

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)

    def update_visuals(self, *args):
        self.prev_selected = BooleanProperty(False)
        if self.selected != self.prev_selected:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.5, 0.8, 0.5, 1) if self.selected else Color(0.5, 0.5, 0.5, 1) # 선택된 경우의 배경색 (녹색)
                Rectangle(pos=self.pos, size=self.size)
            self.prev_selected = self.selected
    
    def on_press(self):
        # 선택 상태 토글
        self.selected = not self.selected
        self.update_visuals()
        app = App.get_running_app()
        song_list_screen = app.root.get_screen('song_list')
        index_int = int(self.index)  # 문자열 인덱스를 정수로 변환
        song_list_screen.select_song(index_int)  # 정수 인덱스 사용
        

    def on_release(self):
        # toggle_selected_state 메서드를 0.5초 후에 실행하도록 스케줄링합니다.
        Clock.schedule_once(self.toggle_selected_state, 0.25)
        
    def toggle_selected_state(self, dt):
        # 실제로 상태를 토글하고 시각적 업데이트를 수행하는 메서드
        self.selected = not self.selected
        self.update_visuals()
        

# Kivy 레이아웃을 정의합니다.
Builder.load_string("""
<ArtistSearchScreen>:
    canvas:
        Color:
            rgba: 0.6, 0.75, 0.6, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text: '멜론 One-Click 플레이리스트 링크생성기'
            size_hint: None, None  # 크기 힌트를 None으로 설정하여 size 값을 직접 제어
            size: self.texture_size  # 텍스트의 크기에 맞게 라벨 크기 조정
            font_name: './nanayang.ttf'
            font_size: 72
            pos_hint: {'center_x': 0.5, 'center_y': 0.8}  # 화면의 상단에 위치

    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, None
        height: self.minimum_height
        pos_hint: {'center_x': 0.5, 'center_y': 0.6}  # 중간보다 살짝 위로 위치
        Label:
            text: '가수 이름을 검색하세요'
            size_hint_y: None
            height: '60dp'
            font_name: './nanayang.ttf'
            font_size: 60
            color: 0, 0, 0, 1
        TextInput:
            id: artist_name_input
            size_hint_y: None
            height: '72dp'
            font_name: './nanayang.ttf'
            font_size: 120
            halign: 'center'
            valign: 'middle'
            multiline: False  # 멀티라인 비활성화
            padding_y: (self.height - self.line_height) / 2  # Y축 패딩으로 수직 중앙 정렬 조정
        Button:
            text: '검색'
            size_hint_y: None
            height: '72dp'
            on_press: root.search_artist()
            font_name: './nanayang.ttf'
            font_size: 72


<SongListScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: '< Back'
            size_hint_y: None
            height: '48dp'
            on_press: app.root.current = 'search'
            font_name: './nanayang.ttf'
            font_size: 72
        TextInput:
            id: search_input
            size_hint_y: None
            height: '48dp'
            multiline: False
            on_text: root.filter_songs(self.text)   
            hint_text: '검색어를 입력하세요'
            font_name: './nanayang.ttf'
            font_size: 72
        RecycleView:
            id: rv
            viewclass: 'SelectableLabel'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                
                canvas:
                    Color:
                        rgba: 0.5, 0.5, 0.5, 1  # 회색 배경색
                    Rectangle:
                        pos: self.pos
                        size: self.size
        Button:
            text: '플레이리스트 >'
            size_hint_y: None
            height: '48dp'
            on_press: root.create_playlist()
            font_name: './nanayang.ttf'
            font_size: 72

<PlaylistScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: '< Back'
            size_hint_y: None
            height: '48dp'
            on_press: app.root.current = 'song_list'
            font_name: './nanayang.ttf'
            font_size: 72
        Button:
            text: '초기화'
            size_hint_y: None
            height: '48dp'
            on_press: root.clear_selection()
            font_name: './nanayang.ttf'
            font_size: 72
        RecycleView:
            id: rv
            viewclass: 'KoreanLabel'
            font_size: 72
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
        Button:
            text: '원클릭! >'
            size_hint_y: None
            height: '48dp'
            on_press: root.show_playlist_urls()
            font_name: './nanayang.ttf'
            font_size: 72
<URLsScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing:10
        Button:
            text: '< Back'
            size_hint_y: None
            height: '48dp'
            on_press: app.root.current = 'playlist'
            font_name: './nanayang.ttf'
            font_size: 72
                    
        ScrollView:
            size_hint: 1, 1  # 부모 위젯에 맞게 크기 조정
            BoxLayout:
                id: url_layout
                orientation: 'vertical'
                size_hint_y: None
                size_hint_x: 1
                height: self.minimum_height
                
        Button:
            text: 'url보기 >'
            size_hint_y: None
            height: 150
            on_release: root.import_urls()
            font_name: './nanayang.ttf'
            font_size: 72

""")

# 아티스트 검색 화면 클래스입니다.
class ArtistSearchScreen(Screen):
    def search_artist(self):
        artist_name = self.ids.artist_name_input.text
        # 비동기 호출을 위한 스레드 생성
        threading.Thread(target=self.fetch_artist_id, args=(artist_name,)).start()

    def fetch_artist_id(self, artist_name):
        try:
            # 가수 ID를 가져오는 요청 수행
            artist_id = artist_id_module.get_artist_id(artist_name)
            if artist_id:
                # UI 업데이트를 위해 메인 스레드에서 실행
                Clock.schedule_once(lambda dt: self.update_ui(artist_id))
            else:
                # 에러 팝업을 메인 스레드에서 표시
                Clock.schedule_once(lambda dt: self.show_error_popup())
        except Exception as e:
            print(e)
            Clock.schedule_once(lambda dt: self.show_error_popup())

    def update_ui(self, artist_id):
        # 검색 결과를 바탕으로 UI 업데이트 로직 구현
        self.manager.get_screen('song_list').artist_id = artist_id
        self.manager.get_screen('song_list').update_songs(artist_id)
        self.manager.current = 'song_list'

    def show_error_popup(self):
        popup = Popup(title='Error', content=Label(text='Artist not found or error occurred.'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

# 노래 목록 화면 클래스입니다.
class SongListScreen(Screen):
    selection = ListProperty([])
    all_songs = ListProperty([])  # 모든 노래 목록 저장
    
    def update_songs(self, artist_id):
        header = {"User-Agent": "Mozilla/5.0"}
        songs = song_info_module.melon_artist_songs(artist_id, header)
        self.all_songs = [{'text': f"{title} - {album}", 'index': str(index), 'songid': songid}
                            for index, (title, songid, album) in enumerate(zip(songs.titles, songs.songids, songs.albums))]
        self.ids.rv.data = self.all_songs  # 초기에는 모든 노래 표시

    def filter_songs(self, search_text):
        if search_text.strip() == '':
            self.ids.rv.data = self.all_songs  # 검색어가 없으면 모든 노래 표시
        else:
            # 검색어가 포함된 노래만 필터링하여 표시
            filtered_songs = [song for song in self.all_songs if search_text.lower() in song['text'].lower()]
            # 필터링된 노래들에 새로운 인덱스 할당
            self.ids.rv.data = [{'text': song['text'], 'index': str(index), 'songid': song['songid']}
                                for index, song in enumerate(filtered_songs)]

    def select_song(self, index):
        # 선택한 노래의 인덱스를 사용하여 해당 노래를 selection 리스트에 추가
        song_data = self.ids.rv.data[index]
        #if song_data not in self.selection:  # 중복 선택을 방지
        self.selection.append(song_data)  # 선택된 노래 추가
            # 선택 상태 업데이트 로직 (선택된 노래를 시각적으로 표시하는 등의 추가 작업이 필요한 경우 여기에 구현)

    def create_playlist(self):
        self.manager.get_screen('playlist').update_playlist()
        self.manager.current = 'playlist'

# 재생목록 화면 클래스입니다.
# PlaylistScreen 클래스 내부
class PlaylistScreen(Screen):
    def __init__(self, **kwargs):
        super(PlaylistScreen, self).__init__(**kwargs)
        self.clear_popup = None  # 팝업 참조를 저장할 속성

    def update_playlist(self):
    # 선택된 노래 목록을 가져옵니다.
        selected_songs = self.manager.get_screen('song_list').selection
    # 선택된 노래를 RecycleView의 데이터로 설정합니다.
        self.ids.rv.data = [{'text': song['text']} for song in selected_songs]
    def show_playlists(self, playlist_urls):
        urls_screen = self.manager.get_screen('urls_screen')
        urls_screen.urls_text = '\n'.join(playlist_urls)
        self.manager.current = 'urls_screen'

    # def show_playlists(self, playlist_urls):
    #     # URL 목록을 팝업으로 표시
    #     url_text = '\n'.join(playlist_urls)
    #     popup = Popup(title='Playlists', content=Label(text=url_text),
    #                   size_hint=(None, None), size=(400, 200))
    #     popup.open()


    def show_playlist_urls(self):
        song_list_screen = App.get_running_app().root.get_screen('song_list')
        selected_songs = song_list_screen.selection
        song_ids = [song['songid'] for song in selected_songs]
        
        urls = self.segment_songs_and_create_urls(song_ids)
        self.manager.get_screen('urls_screen').urls = urls
        self.manager.current = 'urls_screen'
        
        # # URLsScreen으로 전환하고 URL 목록을 표시합니다.
        # urls_screen = self.manager.get_screen('urls_screen')
        # urls_screen.urls_text = '\n'.join(urls)  # URL 목록을 문자열로 변환하여 설정합니다.
        # self.manager.current = 'urls_screen'  # 화면을 URLsScreen으로 변경합니다.


    def clear_selection(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=70)
        content.add_widget(Label(text='선택한 항목을 지우시겠습니까?',font_name='./nanayang.ttf',font_size=72))
        button_layout = BoxLayout(height=150, size_hint_y=None)
        
        confirm_btn = Button(text='확인',font_name='./nanayang.ttf',font_size=48)
        confirm_btn.bind(on_press=self.actual_clear_selection)  # 실제 삭제 실행
        button_layout.add_widget(confirm_btn)
        
        cancel_btn = Button(text='취소',font_name='./nanayang.ttf',font_size=48)
        cancel_btn.bind(on_press=lambda x: self.clear_popup.dismiss())  # 팝업 닫기
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        
        self.clear_popup = Popup(title='Delete All?', content=content,
                                 size_hint=(None, None), size=(800, 600), auto_dismiss=False)
        self.clear_popup.open()

    def actual_clear_selection(self, instance):
        self.manager.get_screen('song_list').selection = []
        self.update_playlist()
        if self.clear_popup:  # 팝업이 존재하는 경우 닫기
            self.clear_popup.dismiss()
            self.clear_popup = None  # 팝업 참조 제거

    def segment_songs_and_create_urls(self, selected_songs):
        # Base URLs for each platform
        base_url_android_ios = "melonapp://play?menuid=0&ctype=1&cid="
        base_url_pc = "melonapp://play/?cType=1&menuId=1000002721&cList="

        # 곡 ID를 담을 세트 초기화
        segmented_lists = []  # 세그먼트 리스트 초기화
        current_segment = []  # 현재 세그먼트 초기화

        for song_id in selected_songs:
            if song_id in current_segment:
                # 현재 세그먼트에 이미 song_id가 있다면 현재 세그먼트를 저장하고 새로운 세그먼트 시작
                segmented_lists.append(current_segment)
                current_segment = [song_id]
            else:
                # 현재 세그먼트에 song_id가 없다면 현재 세그먼트에 추가
                current_segment.append(song_id)
        
        # 마지막 세그먼트 추가
        if current_segment:
            segmented_lists.append(current_segment)

        # 각 세그먼트별로 URL 생성
        android_urls = [base_url_android_ios + ",".join(map(str, segment)) for segment in segmented_lists]
        pc_urls = [base_url_pc + ",".join(map(str, segment)) for segment in segmented_lists]

        # iOS용 URL은 전체 노래 목록을 하나의 링크로 생성
        ios_url = base_url_android_ios + ",".join(map(str, selected_songs))

        return {'android_urls': android_urls, 'ios_url': ios_url, 'pc_urls': pc_urls}

    def create_playlist_urls(self, song_ids):
        urls = self.segment_songs_and_create_urls(song_ids)
        for url in urls:
            print(url)  # Print each URL

    # Show playlist URLs
    def show_playlist_urls(self):
        song_list_screen = App.get_running_app().root.get_screen('song_list')
        selected_songs = song_list_screen.selection
        song_ids = [song['songid'] for song in selected_songs]

        urls = self.segment_songs_and_create_urls(song_ids)
        self.manager.get_screen('urls_screen').urls = urls
        self.manager.current = 'urls_screen'

class URLsScreen(Screen):
    urls = DictProperty({'android_urls': [], 'ios_url': '', 'pc_urls': []})
    android_urls_shortened = ListProperty([])
    ios_url_shortened = StringProperty()
    pc_urls_shortened = ListProperty([])
    popup_shown = BooleanProperty(False)  # 팝업 표시 상태

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_all_urls_shortened')

    def on_all_urls_shortened(self):
        # 모든 URL이 단축되었을 때 호출
        if not self.popup_shown:
            self.show_combined_urls_popup()

    def import_urls(self):
        threading.Thread(target=self.shorten_urls_async_android).start()
        threading.Thread(target=self.shorten_urls_async_pc).start()
        threading.Thread(target=self.shorten_url_async_ios).start()

    def on_pre_enter(self):
        self.ids.url_layout.clear_widgets()

        # Android URLs
        for index, url in enumerate(self.urls['android_urls'], start=1):
            btn = Button(text=f'Android 링크{index}', size_hint_y=None, height=150, font_name='./nanayang.ttf', font_size=100)
            btn.bind(on_release=lambda instance, url=url: webbrowser.open(url))
            self.ids.url_layout.add_widget(btn)

        # iOS URL
        btn_ios = Button(text='iOS 링크', size_hint_y=None, height=150, font_name='./nanayang.ttf', font_size=100)
        btn_ios.bind(on_release=lambda instance, url=self.urls['ios_url']: webbrowser.open(url))
        self.ids.url_layout.add_widget(btn_ios)

        # PC URLs
        for index, url in enumerate(self.urls['pc_urls'], start=1):
            btn_pc = Button(text=f'PC 링크{index}', size_hint_y=None, height=150, font_name='./nanayang.ttf', font_size=100)
            btn_pc.bind(on_release=lambda instance, url=url: webbrowser.open(url))
            self.ids.url_layout.add_widget(btn_pc)

    def shorten_urls_async_android(self):
        shortened_urls_android = []
        for url in self.urls['android_urls']:
            response = requests.get(f"http://tinyurl.com/api-create.php?url={requests.utils.quote(url)}")
            shortened_urls_android.append(response.text)
        self.android_urls_shortened = shortened_urls_android
        self.check_all_done()

    def shorten_urls_async_pc(self):
        shortened_urls_pc = []
        for url in self.urls['pc_urls']:
            response = requests.get(f"http://tinyurl.com/api-create.php?url={requests.utils.quote(url)}")
            shortened_urls_pc.append(response.text)
        self.pc_urls_shortened = shortened_urls_pc
        self.check_all_done()

    def shorten_url_async_ios(self):
        url = self.urls['ios_url']
        response = requests.get(f"http://tinyurl.com/api-create.php?url={requests.utils.quote(url)}")
        if response.status_code == 200:
            self.ios_url_shortened = response.text
        else:
            self.ios_url_shortened = "Error shortening URL"
        self.check_all_done()

    def check_all_done(self):
        if self.android_urls_shortened and self.ios_url_shortened and self.pc_urls_shortened:
            Clock.schedule_once(lambda dt: self.show_combined_urls_popup(), 0)

    def show_combined_urls_popup(self):
        if self.popup_shown:
            return
        self.popup_shown = True

        android_text = 'Android 링크:\n' + '\n'.join(self.android_urls_shortened)
        ios_text = 'iOS 링크:\n' + self.ios_url_shortened
        pc_text = 'PC 링크:\n' + '\n'.join(self.pc_urls_shortened)
        urls_text = '\n\n'.join([android_text, ios_text, pc_text])

        content = BoxLayout(orientation='vertical')
        text_input = TextInput(text=urls_text, readonly=True, font_size=40, size_hint_y=0.9, font_name='./nanayang.ttf')
        copy_button = Button(text='클립보드에 복사', size_hint_y=None, height=150, font_name='./nanayang.ttf', font_size=72)
        copy_button.bind(on_release=lambda instance: Clipboard.copy(text_input.text))
        content.add_widget(text_input)
        content.add_widget(copy_button)

        self.current_popup = Popup(title='Shortened URLs', content=content, size_hint=(0.8, 0.8))
        self.current_popup.open()
        self.current_popup.bind(on_dismiss=self.on_popup_dismiss)

    def on_popup_dismiss(self, instance):
        self.popup_shown = False
        del self.current_popup  # 참조 제거하여 다시 생성 가능하도록

class ImageViewerPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "User's Guide"
        self.images = ['./image1.png', './image2.png', './image3.png', './image4.png', './image5.png'] 
        self.current_index = 0
        self.image_widget = Image(source=self.images[self.current_index], allow_stretch=True)
        self.content = self.image_widget
        self.auto_dismiss = False
        self.size_hint = (1, 1)  # 팝업이 전체 화면을 채우도록 수정
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.current_index += 1
            if self.current_index >= len(self.images):
                self.dismiss()
            else:
                self.image_widget.source = self.images[self.current_index]
            return True
        return super().on_touch_down(touch)

# Modify your main app class or the appropriate screen to include the usage button
class MelonPlaylistApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ArtistSearchScreen(name='search'))
        sm.add_widget(SongListScreen(name='song_list'))
        sm.add_widget(PlaylistScreen(name='playlist'))
        sm.add_widget(URLsScreen(name='urls_screen'))  # Your existing screens
        Clock.schedule_once(lambda dt: self.show_usage_button())
        return sm

    def show_usage_button(self, *args):
        usage_button = Button(text="사용법", size_hint=(None, None), size=(200, 100), font_name='./nanayang.ttf', font_size=72)
        # 버튼 위치를 수정하여 우측 상단으로 이동
        usage_button.pos = (Window.width - usage_button.width - 20, Window.height - usage_button.height - 20)
        # 윈도우 크기 변경 시 버튼 위치 업데이트
        Window.bind(on_resize=lambda instance, width, height: setattr(usage_button, 'pos', (width - usage_button.width - 20, height - usage_button.height - 20)))
        usage_button.bind(on_release=self.show_usage)
        self.root.current_screen.add_widget(usage_button)  # 현재 스크린에 버튼 추가

    def show_usage(self, instance):
        popup = ImageViewerPopup()
        popup.open()

# 애플리케이션을 실행합니다.
if __name__ == '__main__':
    MelonPlaylistApp().run()
